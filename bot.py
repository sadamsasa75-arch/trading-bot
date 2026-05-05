import yfinance as yf
import pandas as pd
import time
import requests

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

symbols = ["EURUSD=X", "GBPUSD=X", "USDJPY=X"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def get_data(symbol):
    return yf.download(symbol, period="1d", interval="1m")

def indicators(df):
    # Bollinger Bands (20,2)
    df['ma20'] = df['Close'].rolling(20).mean()
    df['std'] = df['Close'].rolling(20).std()
    df['upper'] = df['ma20'] + 2 * df['std']
    df['lower'] = df['ma20'] - 2 * df['std']

    # RSI (2)
    delta = df['Close'].diff()
    gain = delta.clip(lower=0).rolling(2).mean()
    loss = -delta.clip(upper=0).rolling(2).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MA50 (فلتر الترند)
    df['ma50'] = df['Close'].rolling(50).mean()

    return df

def signal(df):
    last = df.iloc[-1]

    # CALL
    if (last['Close'] < last['lower'] and
        last['rsi'] < 10 and
        last['Close'] > last['ma50']):
        return "📈 CALL"

    # PUT
    if (last['Close'] > last['upper'] and
        last['rsi'] > 90 and
        last['Close'] < last['ma50']):
        return "📉 PUT"

    return None

def run():
    print("Bot running...")

    while True:
        for sym in symbols:
            try:
                df = get_data(sym)
                df = indicators(df)

                sig = signal(df)

                if sig:
                    msg = f"🔥 {sym} → {sig}"
                    print(msg)
                    send_message(msg)

            except Exception as e:
                print("Error:", e)

        time.sleep(60)

if __name__ == "__main__":
    run()
