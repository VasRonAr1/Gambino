

import logging
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Разрешенные пользователи (по именам)
ALLOWED_USERNAMES = {'SpammBotss'}  # Замените на имена пользователей
# Список зарегистрированных чатов
registered_chats user_id}, username: @{username}")

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
