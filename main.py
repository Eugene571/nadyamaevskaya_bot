from telegram.ext import Application
from bot.handlers import register_handlers
from bot.config import TELEGRAM_TOKEN
from bot.database import init_db


def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    register_handlers(app)
    app.run_polling()


if __name__ == "__main__":
    main()
