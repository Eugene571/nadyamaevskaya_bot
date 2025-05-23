# 🌟 Telegram-бот: Астро-методички от Нади Маевской:
Этот бот помогает пользователям получить авторские PDF-методички по астрологии от Нади Маевской. Он автоматически собирает данные о пользователях, отправляет нужные файлы и предлагает вступить в сообщество. Есть удобный админ-функционал: загрузка и удаление методичек прямо через Telegram.

## 🚀 Возможности
### 👤 Регистрация пользователя
При первом запуске бот задаёт вопросы:
- Имя
- Дата рождения (с подтверждением)
- Номер телефона (с автоматической нормализацией и подтверждением)

После регистрации бот сохраняет данные в базу

### 📚 Получение методичек
- После регистрации или повторного входа пользователь может выбрать одну из доступных PDF-методичек (файлы берутся из папки PDF_DIR)
- Названия кнопок автоматически формируются по названиям PDF-файлов

После получения файла бот отправляет тематические рекомендации и приглашает в Telegram-сообщество

### 🔁 Повторное получение файлов
-После отправки файла бот предлагает выбрать другой или завершить диалог с кнопками «Да / Нет»

### 🔐 Админ-функции
1. 📤 Загрузка новых файлов (/upload)
- Доступно только для админов (список ADMIN_IDS)
- Админ может отправить PDF-файл — он сохранится в PDF_DIR и появится в списке доступных методичек

2. 🗑 Удаление файлов (/delete)
- Также доступно только для админов
- Бот показывает список всех PDF-файлов и позволяет удалить любой из них через нажатие кнопки

### 📂 Структура кода
`handlers.py` — основная логика бота и обработка сообщений

`pdf_utils.py` — отправка PDF пользователю

`database.py` — работа с базой данных (SQLite через SQLAlchemy) # на проде использует postgreSQL

`phone_utils.py` — нормализация номера телефона
