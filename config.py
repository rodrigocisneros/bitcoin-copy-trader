# config.py
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BITCOIN_ADDRESS = os.getenv("BITCOIN_ADDRESS", "1BoatSLRHtKNngkdXEeobR76b53LETtpyT")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))
INITIAL_BTC = float(os.getenv("INITIAL_BTC", 0.0))
INITIAL_USDT = float(os.getenv("INITIAL_USDT", 1000.0))
