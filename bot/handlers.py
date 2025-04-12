from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from bot.pdf_utils import send_pdf_to_user
from bot.database import save_user_data, create_user_if_not_exists, get_user_data
from bot.phone_utils import normalize_phone_number

ASK_NAME, ASK_BIRTHDAY, ASK_PHONE, ASK_FILE_SELECTION = range(4)


# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = update.effective_user.id
    user_data = get_user_data(tg_id)  # Получаем данные пользователя из базы данных

    if user_data:  # Если пользователь существует, сразу переходим к выбору файла
        await update.message.reply_text("Привет, ты уже зарегистрирован!" + " \n " + " \n "
                                        "У меня есть для тебя астро-методички, которые улучшат разные сферы жизни: \n" + "\n"
                                        "1. «ПРОЯВЛЕННОСТЬ» ☀️\nТы узнаешь, как стать заметнее для мира, привлекать удачу и быть уверенным в себе человеком \n" + "\n"
                                        "2. «КАК ВЛЮБИТЬ МУЖЧИНУ» 💖\nИспользуя определенные лайфхаки, ты западаешь возлюбленному в самое сердечко \n" + "\n"
                                        "Напиши номер методички, которую хочешь получить 👇"
                                        )
        return ASK_FILE_SELECTION

    # Если пользователя нет в базе, начинаем собирать данные
    create_user_if_not_exists(tg_id)
    await update.message.reply_text("Привет! Я бот-помощник астролога Нади Маевской 💗\n"+"\n"
                                    "Как тебя зовут?")

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
    await update.message.reply_text("Спасибо, все данные сохранены ✅ \n ")
    await update.message.reply_text("У меня есть для тебя астро-методички, которые улучшат разные сферы жизни: \n" + "\n"
                                    "1. «ПРОЯВЛЕННОСТЬ» ☀️\nТы узнаешь, как стать заметнее для мира, привлекать удачу и быть уверенным в себе человеком \n" + "\n"
                                    
                                    "2. «КАК ВЛЮБИТЬ МУЖЧИНУ» 💖\nИспользуя определенные лайфхаки, ты западаешь возлюбленному в самое сердечко \n" + "\n"
                                    "Напиши номер методички, которую хочешь получить 👇")

    return ASK_FILE_SELECTION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос отменён.")
    return ConversationHandler.END


async def get_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если пользователь ввел номер (1 или 2), отправляем соответствующий файл
    text = update.message.text
    if text == '1':
        filename = "Проявленность.pdf"
    elif text == '2':
        filename = "Как влюбить мужчину.pdf"
    else:
        await update.message.reply_text("Пожалуйста, выбери номер 1 или 2.")
        return

    await send_pdf_to_user(update, context, filename)
    return ConversationHandler.END


# Регистрируем обработчики
def register_handlers(app):
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_birthday)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ASK_FILE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_pdf)],  # Добавляем обработку ввода номера
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conversation_handler)
