from dotenv import load_dotenv
import os

load_dotenv()

print("BOT TOKEN:", os.getenv("TELEGRAM_BOT_TOKEN"))
print("CHAT ID:", os.getenv("TELEGRAM_CHAT_ID"))
