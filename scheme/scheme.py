from pydantic import BaseModel, EmailStr,ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
	name: str
	email:EmailStr
	phone:str
	password:str
	district:str
	
class UserOut(BaseModel):
	id:int
	name:str
	email:EmailStr
	district:str
	role:str
	
	model_config = ConfigDict(from_attributes=True)
	
class Token(BaseModel):
	access_token:str
	token_type:str