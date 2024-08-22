import asyncio
import requests
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)

bot = Bot(token="7533737081:AAGIRW35bfZQjRZEcHtdP9XLTsdBYiDdsOc")
dp = Dispatcher()

user_chat_id = None

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    global user_chat_id
    user_chat_id = message.chat.id
    logging.info(f"User started the bot with chat_id: {user_chat_id}")
    await message.reply("Привет! Я буду отправлять тебе курсы валют и криптовалют каждый день в 8:00, 12:00 и 20:00 по московскому времени.")

async def send_currency_rates():
    global user_chat_id
    if user_chat_id is None:
        logging.warning("No user has started the bot yet.")
        return

    data = requests.get("https://www.cbr-xml-daily.ru/daily_json.js").json()
    bitcoin = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC").json()
    eth = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=ETH").json()

    usd = data['Valute']['USD']['Value']
    eur = data['Valute']['EUR']['Value']
    cny = data['Valute']['CNY']['Value']

    bitcoin_usd = bitcoin['data']['rates']['USD']
    eth_usd = eth['data']['rates']['USD']

    message = f"""
Курс валют

USD - {usd}
EUR - {eur}
CNY - {cny}

Курс криптовалют

BITCOIN - {bitcoin_usd}
ETH - {eth_usd}
"""

    await bot.send_message(chat_id=user_chat_id, text=message)

async def main():
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_currency_rates, trigger='cron', hour=8, minute=0, start_date=datetime.now())
    scheduler.add_job(send_currency_rates, trigger='cron', hour=14, minute=0, start_date=datetime.now())
    scheduler.add_job(send_currency_rates, trigger='cron', hour=20, minute=0, start_date=datetime.now())
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())