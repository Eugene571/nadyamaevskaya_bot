import os
from bot.config import PDF_DIR


async def send_pdf_to_user(update, context, filename):
    file_path = os.path.join(PDF_DIR, filename)
    print("DEBUG: full path =", file_path)  # Выводим полный путь для отладки
    try:
        with open(file_path, "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=filename,
                caption="Вот ваш файл 📄"
            )
    except FileNotFoundError:
        await update.message.reply_text("Файл не найден 😥")
