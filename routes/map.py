import asyncio
from fastapi import APIRouter
from services.weather_service import fetch_weather
from data.kerala_districts import KERALA_DISTRICTS
from data.weather_codes import get_weather_info
from data.severity import get_alert_level

router = APIRouter()

async def _district_weather(name: str, coords: dict):
	result = await fetch_weather(coords["lat"], coords["lon"])
	data = result["weather"]
	current = data["current"]
	rain_prob = data["hourly"]["precipitation_probability"][0] or 0

	alert_level = get_alert_level(
		weather_code=current["weather_code"],
		rain_probability=rain_prob,
		wind_speed=current["wind_speed_10m"],
	)

	return {
		"district": name,
		"latitude": coords["lat"],
		"longitude": coords["lon"],
		"temperature": current["temperature_2m"],
		"humidity": current["relative_humidity_2m"],
		"rain_probability": rain_prob,
		"weather_code": current["weather_code"],
		"weather_label": get_weather_info(current["weather_code"])["label"],
		"wind_speed": current["wind_speed_10m"],
		"wind_direction": current["wind_direction_10m"],
		"wind_gusts": current["wind_gusts_10m"],
		"alert_level": alert_level,
	}

@router.get("/weather/kerala-map")
async def get_kerala_map():
	tasks = [_district_weather(name, coords) for name, coords in KERALA_DISTRICTS.items()]
	results = await asyncio.gather(*tasks, return_exceptions=True)

	districts = [r for r in results if not isinstance(r, Exception)]

	return {"districts": districts}