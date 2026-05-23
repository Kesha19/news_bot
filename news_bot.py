import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("✅ Бот работает 24/7!\n\nКоманды:\n/news — новости\n/price — цены крипты")

@dp.message(Command("news"))
async def news_cmd(message: types.Message):
    await message.answer("🔍 Ищу важные новости...")

@dp.message(Command("price"))
async def price_cmd(message: types.Message):
    await message.answer("💰 Проверяю цены крипты...")

async def main():
    print("🚀 Бот успешно запущен на Render!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
