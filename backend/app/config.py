import json
import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = os.environ.get("DEBUG", "False") == "True"
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")
ORIGINS = json.loads(os.environ.get("ORIGINS", '["http://localhost:3000"]'))
USE_SSL = os.environ.get("USE_SSL", "False") == "True"
DATABASE_URL = os.environ.get("DATABASE_URL").replace("?sslmode=require", "")
SECRET_KEY = os.environ.get("OAUTH_SECRET_KEY")
HASH_ALGORITHM = os.environ.get("OAUTH_HASH_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_SECRET_KEY = os.environ.get("GOOGLE_SECRET_KEY")
EMAIL_LOGIN = os.environ.get("EMAIL_LOGIN")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
SEND_EMAILS = os.environ.get("SEND_EMAILS", "True") == "True"
