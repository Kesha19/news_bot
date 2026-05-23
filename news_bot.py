
import asyncio
import os
import feedparser
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pycoingecko import CoinGeckoAPI
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

cg = CoinGeckoAPI()

chat_id = None
active = True
last_news_titles = set()

KEYWORDS = ["Trump", "Трамп", "Иран", "Iran", "Маска", "Musk", "Elon", "Bitcoin", "BTC", "ETH", "war", "соглашение", "переговоры", "Ормуз", "санкции"]

RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://feeds.feedburner.com/TechCrunch/",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
]

async def get_prices():
    try:
        prices = cg.get_price(ids=['bitcoin', 'ethereum', 'solana'], vs_currencies='usd')
        return f"""💰 Крипто цены:

₿ BTC: ${prices['bitcoin']['usd']:,}
Ξ ETH: ${prices['ethereum']['usd']:,}
◎ SOL: ${prices.get('solana', {}).get('usd', '—'):,}"""
    except:
        return "❌ Цены временно недоступны"

async def fetch_new_news():
    global last_news_titles
    new_news = []
    
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:12]:
            title = entry.title.strip()
            if title in last_news_titles:
                continue
            full_text = (title + " " + entry.summary if hasattr(entry, 'summary') else title).lower()
            if any(kw.lower() in full_text for kw in KEYWORDS):
                last_news_titles.add(title)
                new_news.append(f"📰 {title}\n🔗 {entry.link}")
    
    return new_news[:5]

@dp.message(Command("start"))
async def start(message: types.Message):
    global chat_id
    chat_id = message.chat.id
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📰 Новости сейчас", callback_data="news")],
        [InlineKeyboardButton(text="💰 Цены сейчас", callback_data="price")],
        [InlineKeyboardButton(text="⏹️ Стоп", callback_data="stop")],
        [InlineKeyboardButton(text="▶️ Запустить", callback_data="start")],
    ])
    
    await message.answer("✅ **Бот в максимально быстром режиме!**\nПроверка новостей каждые 2 минуты.", reply_markup=kb)

@dp.callback_query()
async def handler(callback: types.CallbackQuery):
    if callback.data == "news":
        await callback.answer("Поиск...")
        news = await fetch_new_news()
        text = "\n\n".join(news) if news else "Новых новостей пока нет."
        await callback.message.answer(text)
    elif callback.data == "price":
        await callback.answer("Загрузка...")
        await callback.message.answer(await get_prices())
    elif callback.data == "stop":
        global active
        active = False
        await callback.answer("Автообновления остановлены")
    elif callback.data == "start":
        global active
        active = True
        await callback.answer("Автообновления запущены")

async def auto_sender():
    global chat_id, active
    while True:
        if chat_id and active:
            try:
                news = await fetch_new_news()
                if news:
                    await bot.send_message(chat_id, "🚨 Новые новости 🚨\n\n" + "\n\n".join(news))
                
                # Цены каждые 30 минут
                if datetime.now().minute % 30 == 0:
                    await bot.send_message(chat_id, await get_prices())
            except:
                pass
        await asyncio.sleep(120)  # каждые 2 минуты

async def main():
    asyncio.create_task(auto_sender())
    print("Бот запущен — проверка каждые 2 минуты")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
