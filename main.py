from telegram.ext import Application
from bot.handlers import register_handlers
from bot.config import TELEGRAM_TOKEN
from bot.database import init_db

import logging
from telegram.ext import ContextTypes

# Логирование ошибок
logging.basicConfig(level=logging.INFO)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Exception while handling update:", exc_info=context.error)


def main():
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    register_handlers(app)  # Регистрируем все хендлеры

    app.add_error_handler(error_handler)  # Регистрируем обработчик ошибок ⬅️ вот здесь

    app.run_polling()  # Запускаем бота


if __name__ == "__main__":
    main()
