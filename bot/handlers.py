from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from bot.pdf_utils import send_pdf_to_user
from bot.database import save_user_data, create_user_if_not_exists
from bot.phone_utils import normalize_phone_number

ASK_NAME, ASK_BIRTHDAY, ASK_PHONE = range(3)


# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    create_user_if_not_exists(tg_id)
    await update.message.reply_text("Привет! Как тебя зовут?")
    return ASK_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Укажи дату рождения (в формате ДД.ММ.ГГГГ)")
    return ASK_BIRTHDAY


async def get_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["birthday"] = update.message.text
    await update.message.reply_text("И наконец, твой номер телефона:")
    return ASK_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_phone = update.message.text
    phone = normalize_phone_number(raw_phone)
    if not phone:
        await update.message.reply_text("Не удалось распознать номер. Попробуй ещё раз:")
        return ASK_PHONE

    tg_id = update.effective_user.id
    save_user_data(
        tg_id,
        name=context.user_data["name"],
        birthday=context.user_data["birthday"],
        phone=phone,
    )
    await update.message.reply_text("Спасибо, все данные сохранены ✅")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос отменён.")
    return ConversationHandler.END


async def get_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_pdf_to_user(update, context, "Love.pdf")


# Регистрируем обработчики
def register_handlers(app):
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_birthday)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conversation_handler)
    app.add_handler(CommandHandler("get_pdf", get_pdf))
