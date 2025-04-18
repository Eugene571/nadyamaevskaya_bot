from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from bot.pdf_utils import send_pdf_to_user
from bot.database import save_user_data, create_user_if_not_exists, get_user_data
from bot.phone_utils import normalize_phone_number
from bot.database import get_session, User
import httpx

timeout = httpx.Timeout(60.0)  # Установка тайм-аута в 60 секунд
client = httpx.AsyncClient(timeout=timeout)

ASK_NAME, ASK_BIRTHDAY, CONFIRM_BIRTHDAY, ASK_PHONE, CONFIRM_PHONE, ASK_FILE_SELECTION = range(6)


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
                                        )
        keyboard = ReplyKeyboardMarkup([
            ["«ПРОЯВЛЕННОСТЬ» ☀️"],
            ["«КАК ВЛЮБИТЬ МУЖЧИНУ» 💖"]
        ], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "Выбери методичку, которую хочешь получить 👇",
            reply_markup=keyboard
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

    # Кнопки подтверждения
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ДА", callback_data="confirm_birthday_yes")],
        [InlineKeyboardButton("НЕТ", callback_data="confirm_birthday_no")]
    ])
    await update.message.reply_text(
        f"Твоя дата рождения {context.user_data['birthday']}, верно?",
        reply_markup=keyboard
    )
    return CONFIRM_BIRTHDAY


async def confirm_birthday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_birthday_yes":
        await query.message.reply_text("Теперь укажи номер телефона:")
        return ASK_PHONE
    else:
        await query.message.reply_text("Хорошо, укажи дату рождения ещё раз (ДД.ММ.ГГГГ):")
        return ASK_BIRTHDAY


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_phone = update.message.text
    phone = normalize_phone_number(raw_phone)

    if not phone:
        await update.message.reply_text("Не удалось распознать номер. Попробуй ещё раз:")
        return ASK_PHONE

    context.user_data["phone"] = phone

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("ДА", callback_data="confirm_phone_yes")],
        [InlineKeyboardButton("НЕТ", callback_data="confirm_phone_no")]
    ])
    await update.message.reply_text(
        f"Твой номер телефона {phone}, верно?",
        reply_markup=keyboard
    )
    return CONFIRM_PHONE


async def confirm_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "confirm_phone_yes":
        tg_id = query.from_user.id
        save_user_data(
            tg_id,
            name=context.user_data["name"],
            birthday=context.user_data["birthday"],
            phone=context.user_data["phone"],
        )
        await query.message.reply_text("Спасибо!🥰")

        keyboard = ReplyKeyboardMarkup([
            ["«ПРОЯВЛЕННОСТЬ» ☀️"],
            ["«КАК ВЛЮБИТЬ МУЖЧИНУ» 💖"]
        ], resize_keyboard=True, one_time_keyboard=True)

        await query.message.reply_text(
            "Выбери методичку, которую хочешь получить 👇",
            reply_markup=keyboard
        )
        return ASK_FILE_SELECTION

    else:
        await query.message.reply_text("Укажи номер телефона ещё раз:")
        return ASK_PHONE


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
        keyboard = ReplyKeyboardMarkup([
            ["«ПРОЯВЛЕННОСТЬ» ☀️"],
            ["«КАК ВЛЮБИТЬ МУЖЧИНУ» 💖"]
        ], resize_keyboard=True, one_time_keyboard=True)

        await query.message.reply_text(
            "Выбери другую методичку 👇",
            reply_markup=keyboard
        )
        return ASK_FILE_SELECTION

    elif query.data == 'no':
        await query.message.reply_text(
            "Приятного изучения! Будет полезно🤩\n\nЕсли захочешь получить другую методичку — напиши /start"
        )
        return ConversationHandler.END


async def get_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    tg_id = update.effective_user.id

    # Получаем данные пользователя из базы
    with get_session() as session:
        user_data = session.query(User).filter_by(tg_id=tg_id).first()

    # Определяем, какой файл отправить
    if text in ['1', '«ПРОЯВЛЕННОСТЬ» ☀️']:
        filename = "Проявленность.pdf"
        file_id = '1'
    elif text in ['2', '«КАК ВЛЮБИТЬ МУЖЧИНУ» 💖']:
        filename = "Как влюбить мужчину.pdf"
        file_id = '2'
    else:
        await update.message.reply_text("Пожалуйста, выбери методичку из списка.")
        return ASK_FILE_SELECTION

    await send_pdf_to_user(update, context, filename)

    # Отправка рекомендаций (если ещё не получал)
    if not user_data.has_received_pdf:
        if file_id == '1':
            await update.message.reply_text("Используй рекомендации и сияй! ✨\n\n"
                                            "И присоединяйся в наше дружное сообщество. Там море полезностей от меня: ежедневные прогнозы, подкасты и ещё больше астро-методичек 👇🏻\n\n" + "Ты всё найдешь в закреплённом посте \"Навигация\"" + "\n"
                                                                                                                                                                                                                                                  "\nhttps://t.me/nadyamaevskayaa"
                                            )
        elif file_id == '2':
            await update.message.reply_text(
                "Удачи в любви! 💕\n\n"
                "И присоединяйся в наше дружное сообщество. Там море полезностей от меня: ежедневные прогнозы, подкасты и ещё больше астро-методичек ✨👇🏻\n\n" + "Ты всё найдешь в закреплённом посте \"Навигация\"" + "\n"
                                                                                                                                                                                                                      "\nhttps://t.me/nadyamaevskayaa"
            )
        with get_session() as session:
            user_in_session = session.query(User).filter_by(tg_id=tg_id).first()
            user_in_session.has_received_pdf = True
            session.commit()

    # После отправки PDF — inline-кнопки Да/Нет
    await update.message.reply_text("Хочешь получить другой файл?", reply_markup=InlineKeyboardMarkup([
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
            CONFIRM_BIRTHDAY: [CallbackQueryHandler(confirm_birthday, pattern='^confirm_birthday_')],
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            CONFIRM_PHONE: [CallbackQueryHandler(confirm_phone, pattern='^confirm_phone_')],
            ASK_FILE_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_pdf),
                CallbackQueryHandler(handle_file_selection, pattern='^(yes|no)$')
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Только один handler: ConversationHandler
    app.add_handler(conversation_handler)
