from fastapi import fastapi
from database import Base , engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
	return{
	"message": "Kerala Disaster Management App By Websinaro Is Running"
	}