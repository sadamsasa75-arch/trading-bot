import os, asyncio, yfinance as yf, pandas as pd, pytz, ta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

def get_signal():
    df = yf.download("BTC-USD", period="7d", interval="1h")
    c = df['Close']; rsi = ta.momentum.RSIIndicator(c).rsi().iloc[-1]
    bb = ta.volatility.BollingerBands(c); p = c.iloc[-1]
    if p < bb.bollinger_lband().iloc[-1] and rsi < 30: return f"شراء 🟢 {p:.0f}"
    if p > bb.bollinger_hband().iloc[-1] and rsi > 70: return f"بيع 🔴 {p:.0f}"

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("شغال ✅")

async def job(app):
    s = get_signal()
    if s: await app.bot.send_message(CHAT_ID, s)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    sch = AsyncIOScheduler(timezone=pytz.timezone('Asia/Riyadh'))
    sch.add_job(job, 'interval', hours=1, args=[app]); sch.start()
    print("✅ شغال"); await app.run_polling()

if __name__ == '__main__': asyncio.run(main())
