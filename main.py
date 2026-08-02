from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from database.database import Base , engine
from routes import auth,weather
from alembic.config import Config
from alembic import command
import traceback
from middleware.encryption_middleware import EncryptionMiddleware

def run_migrations():
	alembic_cfg = Config("alembic.ini")
	command.upgrade(alembic_cfg, "head")

run_migrations()

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router,tags=["Auth"])
app.include_router(weather.router, tags=["Weather"])
app.add_middleware(EncryptionMiddleware)


# TEMPORARY: remove this once login is confirmed working.
# Exposes real Python errors in the response instead of a blank 500.
@app.exception_handler(Exception)
async def debug_exception_handler(request: Request, exc: Exception):
	return JSONResponse(
		status_code=500,
		content={"error": str(exc), "trace": traceback.format_exc()}
	)

@app.get("/")
def home():
	return{
	"message": "Kerala Disaster Management App By Websinaro Is Running"
	}
