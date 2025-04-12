from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from bot.pdf_utils import send_pdf_to_user


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот и могу прислать тебе PDF.")


async def get_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_pdf_to_user(update, context, "Love.pdf")


def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get_pdf", get_pdf))
