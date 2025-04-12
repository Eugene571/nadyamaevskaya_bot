from telegram.ext import Application
from bot.handlers import register_handlers
from bot.config import TELEGRAM_TOKEN


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    register_handlers(app)
    app.run_polling()


if __name__ == "__main__":
    main()