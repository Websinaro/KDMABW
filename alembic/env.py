from database.database import Base
from config.config import DATABASE_URL
from model import model

target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", DATABASE_URL)
