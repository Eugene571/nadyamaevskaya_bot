
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.pdf_utils import send_pdf_to_user
from bot.database import save_user_data, create_user_if_not_exists, get_user_data
from bot.phone_utils import normalize_phone_number
from bot.database import get_session, User

ASK_NAME, ASK_BIRTHDAY, ASK_PHONE, ASK_FILE_SELECTION = range(4)


# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("FULL UPDATE:", update)
    print("Received /start command, update.message:", update.message)
    tg_id = update.effective_user.id
    user_data = get_user_data(tg_id)  # Получаем данные пользователя из базы данных

    # Логируем, что команда /start была получена
    print(f"Received /start command from {tg_id}")

    if user_data:  # Если пользователь существует, сразу переходим к выбору файла
        name = user_data["name"]
        await update.message.reply_text(f"Привет, {name}! Ты уже зарегистрирован(а)!" + " \n " + " \n "
                                        "У меня есть для тебя астро-методички, которые улучшат разные сферы жизни: \n" + "\n"
                                        "1. «ПРОЯВЛЕННОСТЬ» ☀️\nТы узнаешь, как стать заметнее для мира, привлекать удачу и быть уверенным в себе человеком \n" + "\n"
                                        "2. «КАК ВЛЮБИТЬ МУЖЧИНУ» 💖\nИспользуя определенные лайфхаки, ты западаешь возлюбленному в самое сердечко \n" + "\n"
                                        "Напиши номер методички, которую хочешь получить 👇"
                                        )
        return ASK_FILE_SELECTION

    # Если пользователя нет в базе, начинаем собирать данные
    create_user_if_not_exists(tg_id)
    await update.message.reply_text("Привет! Я бот-помощник астролога Нади Маевской 💗\n" + "\n"
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
    await update.message.reply_text("Спасибо!🥰 \n ")
    await update.message.reply_text(
        "У меня есть для тебя астро-методички, которые улучшат разные сферы жизни: \n" + "\n"
        "1. «ПРОЯВЛЕННОСТЬ» ☀️\nТы узнаешь, как стать заметнее для мира, привлекать удачу и быть уверенным в себе человеком \n" + "\n"
        "2. «КАК ВЛЮБИТЬ МУЖЧИНУ» 💖\nИспользуя определенные лайфхаки, ты западаешь возлюбленному в самое сердечко \n" + "\n"
        "Напиши номер методички, которую хочешь получить 👇")

    return ASK_FILE_SELECTION


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Опрос отменён.")
    # Очистить состояние после завершения
    return ConversationHandler.END


async def handle_file_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # <<< это обязательно

    tg_id = query.from_user.id
    print(f"Button clicked: {query.data}")

    if query.data == 'yes':
        await query.message.reply_text("Введи номер нужной методички (1 или 2):")
        return ASK_FILE_SELECTION
    elif query.data == 'no':
        await query.message.reply_text("Приятного изучения! Будет полезно🤩")
        return ConversationHandler.END


async def get_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    tg_id = update.effective_user.id

    # Получаем данные пользователя из базы
    with get_session() as session:
        user_data = session.query(User).filter_by(tg_id=tg_id).first()

    # Определяем, какой файл отправить
    if text == '1':
        filename = "Проявленность.pdf"
    elif text == '2':
        filename = "Как влюбить мужчину.pdf"
    else:
        await update.message.reply_text("Пожалуйста, выбери номер астро-методички.")
        return

    # Если это первый PDF, отправляем сообщение с рекомендациями и ссылкой на канал
    if not user_data.has_received_pdf:
        # Отправляем сообщение с рекомендациями и ссылкой на канал
        await update.message.reply_text(
            "Используй рекомендации и сияй! \n\n"
            "И присоединяйся в наше дружное сообщество. Там море полезностей от меня: ежедневные прогнозы, подкасты и ещё больше астро-методичек ✨👇🏻\n\n"
            "https://t.me/nadyamaevskayaa"
        )

        # Обновляем флаг в базе, что пользователь получил PDF
        with get_session() as session:
            user_in_session = session.query(User).filter_by(tg_id=tg_id).first()
            user_in_session.has_received_pdf = True  # Вот эта строка важна
            session.commit()

    # Отправляем PDF
    await send_pdf_to_user(update, context, filename)

    # Спрашиваем, хочет ли он получить другой файл
    await update.message.reply_text("Хотите получить другой файл?", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("Да", callback_data='yes')],
        [InlineKeyboardButton("Нет", callback_data='no')]
    ]))

    return ASK_FILE_SELECTION


def register_handlers(app):
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            ASK_BIRTHDAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_birthday)],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ASK_FILE_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_pdf),
                CallbackQueryHandler(handle_file_selection, pattern='^(yes|no)$')  # <-- оставить только здесь
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Только один handler: ConversationHandler
    app.add_handler(conversation_handler)

