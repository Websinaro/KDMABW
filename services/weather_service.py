import asyncio
import logging

import httpx
from fastapi import HTTPException

logger = logging.getLogger("weather_service")

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/reverse"

# Same protection routes/map.py already uses for its 14-district burst:
# cap how many /weather requests are in flight to Open-Meteo at once so a
# burst (e.g. the districts overview screen firing 14 calls at once) doesn't
# get itself rate-limited / erroring under load.
_semaphore = asyncio.Semaphore(5)

async def _get_with_retry(client: httpx.AsyncClient, url: str, params: dict, attempts: int = 3):
	"""GET with a couple of retries on transient failures (timeouts, 429s, 5xx)."""
	last_exc = None
	for attempt in range(attempts):
		try:
			async with _semaphore:
				resp = await client.get(url, params=params)
			resp.raise_for_status()
			return resp
		except (httpx.TransportError, httpx.HTTPStatusError) as exc:
			last_exc = exc
			# Don't retry on client errors that a retry won't fix (bad params etc.)
			if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code < 500 and exc.response.status_code != 429:
				break
			if attempt < attempts - 1:
				await asyncio.sleep(0.75 * (attempt + 1))
	logger.warning("Open-Meteo request failed after retries: %s %s", url, last_exc)
	raise last_exc

async def fetch_weather(lat: float, lon: float):
	weather_params = {
		"latitude": lat,
		"longitude": lon,
		"current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,pressure_msl,wind_speed_10m,wind_direction_10m,wind_gusts_10m,uv_index,is_day",
		"hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,precipitation,weather_code,wind_speed_10m,wind_gusts_10m,uv_index,dew_point_2m,visibility",
		"daily": "weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,uv_index_max,precipitation_sum,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max",
		"timezone": "Asia/Kolkata",
		"forecast_days": 7,
	}

	air_params = {
		"latitude": lat,
		"longitude": lon,
		"current": "us_aqi,pm2_5,pm10,ozone,carbon_monoxide",
		"timezone": "Asia/Kolkata",
	}

	geocode_params = {
		"latitude": lat,
		"longitude": lon,
		"language": "en",
	}

	async with httpx.AsyncClient(timeout=10.0) as client:
		# This is the one call that matters - if it fails after retries, surface
		# a clean 503 instead of letting an httpx exception bubble up as a bare,
		# undiagnosable 500.
		try:
			weather_resp = await _get_with_retry(client, WEATHER_URL, weather_params)
		except (httpx.TransportError, httpx.HTTPStatusError) as exc:
			logger.error("Weather fetch failed for lat=%s lon=%s: %s", lat, lon, exc)
			raise HTTPException(
				status_code=503,
				detail="Weather service is temporarily unavailable. Please try again in a moment.",
			)

		place_name = None
		try:
			geo_resp = await _get_with_retry(client, GEOCODE_URL, geocode_params, attempts=1)
			geo_data = geo_resp.json()
			if geo_data.get("results"):
				top = geo_data["results"][0]
				place_name = f"{top.get('name', '')}, {top.get('admin1', '')}"
		except Exception:
			place_name = None

		try:
			air_resp = await _get_with_retry(client, AIR_QUALITY_URL, air_params, attempts=1)
			air_data = air_resp.json()
		except Exception:
			air_data = None

		return {"weather": weather_resp.json(), "air": air_data, "place_name": place_name}

async def fetch_current_only(lat: float, lon: float):
	params = {
		"latitude": lat,
		"longitude": lon,
		"current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
		"hourly": "precipitation_probability",
		"timezone": "Asia/Kolkata",
		"forecast_days": 1,
	}
	async with httpx.AsyncClient(timeout=15.0) as client:
		resp = await client.get(WEATHER_URL, params=params)
		resp.raise_for_status()
		return resp.json()
