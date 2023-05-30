from dotenv import load_dotenv
import os

load_dotenv()

fred_key = os.environ.get("fred_key")
finnhub_key = os.environ.get("finnhub_key")
