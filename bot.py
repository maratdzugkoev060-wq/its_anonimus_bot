import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Токен берётся из переменной окружения на сервере
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8630055474:AAFESgsKtvMCK_3iQiAi63ja3_nC4kaAL98')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "✅ *Бот работает!*\n\n"
        "Если вы это видите — проблема не в подключении.\n"
        "Теперь можно возвращать полноценный код.",
        parse_mode="Markdown"
    )

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"📨 Вы написали: `{message.text}`", parse_mode="Markdown")

async def main():
    print("🚀 Бот запущен и слушает сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())