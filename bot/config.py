import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PDF_DIR = os.getenv("PDF_DIR", "pdfs/")
DB_URL = os.getenv("DB_URL", "sqlite:///bot.db")