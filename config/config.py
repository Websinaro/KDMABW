import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM","HS256")
ACCESS_TOKEN_EXPIRES_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES",60))

# Anyone who signs up while supplying this code as `access_code` is granted
# the "president" role instead of the default "user" role. Change this via
# the PRESIDENT_ACCESS_CODE environment variable on Render and share it only
# with the actual President / State Coordinator account holder(s).
PRESIDENT_ACCESS_CODE = os.getenv("PRESIDENT_ACCESS_CODE", "KDMA-PRESIDENT-2026")