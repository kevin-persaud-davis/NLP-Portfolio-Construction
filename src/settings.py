import os
from dotenv import load_dotenv, find_dotenv

env_path = find_dotenv()

load_dotenv(dotenv_path=env_path)

CONSUMER_KEY = os.getenv("consumer_key")
CONSUMER_SECRET = os.getenv("consumer_secret")

DATABASE_PASSWORD = os.getenv("database_password")

IEX_TOKEN = os.getenv("iex_token")