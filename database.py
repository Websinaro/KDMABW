from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from log import get_logger

from config import DATABASE_URL

logger = get_logger(__name__)

engine = create_engine(DATABASE_URL)

SessionLocal = seccionmaker(
	autocommit=False,
	autoflush=False,
	bind=engine
)

Base = declarative_base()

def get_db():
	db = SessionLocal()
	try:
		yield db
	except:
		logger.warning("Database Error : : : : : : ")
	finally:
		db.close()