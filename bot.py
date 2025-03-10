

import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Разрешенные пользователи (по именам)
ALLOWED_USERNAMES = {'username1', 'username2'}  # Замените на имена пользователей
# Список зарегистрированных чатов
registered_chats = []

# Логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Файл для сохранения списка чатов
CHATS_FILE = 'registered_chats.json'


# Функция для сохранения чатов в файл (формат JSON)
def save_registered_chats():
    with open(CHATS_FILE, 'w') as f:
        json.dump(registered_chats, f, indent=4)


# Функция для загрузки списка чатов из файла (формат JSON)
def load_registered_chats():
    global registered_chats
    if os.path.exists(CHATS_FILE):
        with open(CHATS_FILE, 'r') as f:
            registered_chats = json.load(f)


# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        return

    user_id = update.effective_user.id
    username = update.effective_user.username  # @username без @
    logging.info(f"Получена команда /start от пользователя ID: {user_id}, username: @{username}")

    # Проверяем, есть ли @username пользователя в списке разрешённых
    if username not in ALLOWED_USERNAMES:
        # Сообщение на немецком
        await update.message.reply_text(
            "Hallo, möchtest du auch so einen Bot? "
            "Schreib mir @SpammBotss, du kannst ihn einen Tag lang kostenlos ausprobieren."
        )
        return

    # Обновление списка чатов
    registered_chats.clear()  # Очистка текущего списка чатов
    # Получаем чаты, в которых бот присутствует
    async for chat in context.bot.get_my_chats():
        registered_chats.append({'chat_id': chat.id, 'title': chat.title or str(chat.id)})

    save_registered_chats()  # Сохраняем обновленный список чатов

    # Если чаты найдены, отправляем сообщение во все чаты
    if registered_chats:
        for chat in registered_chats:
            try:
                await context.bot.send_message(chat_id=chat['chat_id'], text="Привет, это тестовое сообщение!")
                logging.info(f"✅ Сообщение отправлено в чат {chat['title']} ({chat['chat_id']})")
            except Exception as e:
                logging.error(f"❌ Сообщение не отправлено в чат {chat['title']} ({chat['chat_id']}): {e}")

    # Если пользователь в списке разрешённых, показываем кнопки
    keyboard = [
        [
            InlineKeyboardButton("📂 Chats ansehen", callback_data='view_chats'),
            InlineKeyboardButton("📤 Nachricht senden", callback_data='send_message'),
        ],
        [
            InlineKeyboardButton("🛑 Verteilung stoppen", callback_data='stop_broadcast'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📋 Wählen Sie eine Aktion:",
        reply_markup=reply_markup
    )


# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Используйте команду /start для начала работы с ботом.')


# Обработка нажатий на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'view_chats':
        await query.edit_message_text(text="Список чатов:\n" + "\n".join([f"{chat['chat_id']}: {chat['title']}" for chat in registered_chats]))
    
    elif query.data == 'send_message':
        await query.edit_message_text(text="Введите сообщение для рассылки.")
    
    elif query.data == 'stop_broadcast':
        await query.edit_message_text(text="Рассылка сообщений остановлена.")


# Основная функция для запуска бота
def main():
    load_registered_chats()  # Загружаем список чатов

    # Создаем приложение и добавляем обработчики
    application = Application.builder().token('7667346265:AAEKmPhrz15Rr1IvhSFSphv8fedtVBKabE8').build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Обработчик нажатий на кнопки
    application.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
