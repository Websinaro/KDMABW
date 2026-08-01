from fastapi import FastAPI
from database.database import Base , engine
from routes import auth
from alembic.config import Config
from alembic import command

def run_migrations():
	alembic_cfg = Config("alembic.ini")
	command.upgrade(alembic_cfg, "head")

run_migrations()

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router,tags=["Auth"])

@app.get("/")
def home():
	return{
	"message": "Kerala Disaster Management App By Websinaro Is Running"
	}
