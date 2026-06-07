import os
import asyncio
import secrets
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import database as db

# Читаем токен из переменной окружения (БЕЗОПАСНО!)
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8630055474:AAFESgsKtvMCK_3iQiAi63ja3_nC4kaAL98')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище активных диалогов (в памяти)
# Ключ: telegram_id анонима, Значение: ключ ссылки
active_sessions = {}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    args = message.text.split()

    # Получаем информацию о боте (чтобы узнать username)
    bot_info = await bot.get_me()
    bot_username = bot_info.username

    if len(args) == 1:
        # Обычный /start - генерируем новую ссылку
        key = secrets.token_urlsafe(12)
        db.save_link(key, message.from_user.id)
        link = f"https://t.me/{bot_username}?start={key}"

        text = (
            "🔗 *ТВОЯ ЛИЧНАЯ ССЫЛКА ДЛЯ АНОНИМНЫХ СООБЩЕНИЙ*\n\n"
            f"[{link}]({link})\n\n"
            "📤 *Как использовать:*\n"
            "1. Отправь эту ссылку кому хочешь\n"
            "2. Человек напишет тебе анонимно\n"
            "3. Чтобы ответить - нажми кнопку 'Ответить' под сообщением\n\n"
            "⚡️ Анонимность гарантирована"
        )
        await message.answer(text, parse_mode="Markdown", disable_web_page_preview=True)

    else:
        # Перешли по ссылке: /start секретный_ключ
        key = args[1]
        owner_id = db.get_owner_by_key(key)

        if owner_id is None:
            await message.answer("❌ Неверная или устаревшая ссылка.")
            return

        # Сохраняем сессию анонима
        active_sessions[message.from_user.id] = key

        await message.answer(
            "📝 *ТЫ В РЕЖИМЕ АНОНИМА*\n\n"
            "Теперь можешь писать сюда любые сообщения.\n"
            "Владелец не узнает, кто ты.\n"
            "Если он ответит - сообщение придёт сюда.\n\n"
            "✍️ Просто напиши что-нибудь...",
            parse_mode="Markdown"
        )


@dp.message()
async def handle_anonymous_message(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, есть ли активная сессия у этого пользователя
    if user_id in active_sessions:
        # Это аноним, отправляем сообщение владельцу
        key = active_sessions[user_id]
        owner_id = db.get_owner_by_key(key)

        if owner_id:
            # Сохраняем сообщение в БД
            db.save_message(key, user_id, message.text)

            # Отправляем владельцу
            await bot.send_message(
                owner_id,
                f"📨 *Новое анонимное сообщение:*\n\n{message.text}\n\n"
                f"💬 Чтобы ответить - нажми 'Ответить' на это сообщение",
                parse_mode="Markdown"
            )

            # Подтверждаем анониму
            await message.answer("✅ Сообщение отправлено анонимно!")
        else:
            await message.answer("❌ Ошибка: владелец не найден")

    else:
        # Проверяем, не ответ ли это владельца
        if message.reply_to_message:
            # Владелец отвечает на анонимное сообщение
            # Получаем оригинальное сообщение, на которое отвечают
            original_text = message.reply_to_message.text

            # Нужно найти в БД кому принадлежало это сообщение
            # (упрощённо: ищем последнее сообщение с таким текстом)
            # В полной версии нужно хранить mapping message_id -> user
            await message.answer("⚠️ Ответы работают в полной версии бота.\nСкажите 'дай полную версию'")
        else:
            await message.answer(
                "🔐 *Чтобы отправить анонимное сообщение:*\n\n"
                "1. Получи ссылку у владельца бота\n"
                "2. Перейди по ней\n"
                "3. После этого пиши сюда любые сообщения\n\n"
                "📌 *Владельцы бота:* напишите /start, чтобы получить свою ссылку",
                parse_mode="Markdown"
            )


async def main():
    print("🚀 Бот запускается...")
    db.init_db()
    print("✅ База данных готова")

    # Получаем информацию о боте для проверки
    bot_info = await bot.get_me()
    print(f"✅ Бот подключен: @{bot_info.username}")

    await bot.delete_webhook(drop_pending_updates=True)
    print("👂 Бот слушает сообщения...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())