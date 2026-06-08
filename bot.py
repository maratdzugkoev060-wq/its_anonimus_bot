import os
import asyncio
import secrets
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import database as db

# Токен берётся из переменной окружения (на сервере Bothost)
# Для локальной проверки временно замените на свой токен
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8630055474:AAFESgsKtvMCK_3iQiAi63ja3_nC4kaAL98')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище активных сессий (аноним → ключ ссылки)
active_sessions = {}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    args = message.text.split()

    # Получаем username бота для создания ссылки
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    if len(args) == 1:
        # Обычный /start — создаём новую ссылку
        key = secrets.token_urlsafe(12)
        db.save_link(key, message.from_user.id)
        link = f"https://t.me/{bot_username}?start={key}"

        text = (
            f"🔗 Твоя личная ссылка для анонимных сообщений:\n\n"
            f"{link}\n\n"
            "Отправь её кому хочешь.\n"
            "Все сообщения, которые придут по этой ссылке, будут анонимными."
        )
        await message.answer(text, disable_web_page_preview=True)

    else:
        # Перешли по ссылке /start КЛЮЧ
        key = args[1]
        owner_id = db.get_owner_by_key(key)

        if owner_id is None:
            await message.answer("❌ Неверная или устаревшая ссылка.")
            return

        # Сохраняем, что этот пользователь теперь аноним
        active_sessions[message.from_user.id] = key
        await message.answer(
            "📝 Ты в режиме анонима!\n\n"
            "Теперь можешь писать сюда любые сообщения.\n"
            "Владелец не узнает, кто ты.\n"
            "Если он ответит — сообщение придёт сюда."
        )


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, есть ли у пользователя активная сессия
    if user_id in active_sessions:
        key = active_sessions[user_id]
        owner_id = db.get_owner_by_key(key)

        if owner_id:
            # Сохраняем сообщение в базу
            db.save_message(key, user_id, message.text)

            # Отправляем владельцу
            await bot.send_message(
                owner_id,
                f"📨 *Новое анонимное сообщение:*\n\n{message.text}\n\n"
                f"💬 Чтобы ответить — просто нажми 'Ответить' на это сообщение.",
                parse_mode="Markdown"
            )

            # Подтверждаем анониму
            await message.answer("✅ Сообщение отправлено анонимно!")
        else:
            await message.answer("❌ Ошибка: владелец не найден")

    else:
        # Проверяем, не ответ ли это от владельца
        if message.reply_to_message:
            # Здесь будет логика ответов анониму
            await message.answer(
                "⚠️ Функция ответов настраивается.\n"
                "Пока что просто получите свою ссылку через /start"
            )
        else:
            await message.answer(
                "🔐 Чтобы отправить анонимное сообщение:\n\n"
                "1. Попроси у владельца бота его личную ссылку\n"
                "2. Перейди по ней\n"
                "3. После этого пиши сюда любые сообщения\n\n"
                "📌 Если ты владелец — напиши /start, чтобы получить ссылку."
            )


async def main():
    print("🚀 Бот запускается...")
    db.init_db()
    print("✅ База данных готова")

    # Проверяем подключение
    bot_info = await bot.get_me()
    print(f"✅ Бот подключен: @{bot_info.username}")

    await bot.delete_webhook(drop_pending_updates=True)
    print("👂 Бот слушает сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())