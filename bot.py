import requests
import time

# =========================
# TELEGRAM SETTINGS
# =========================

TOKEN = "8871701058:AAEdXKgLcJGznFY4NA-Rc2WoqgKsjvUsYkY"
CHAT_ID = "6384233386"

# =========================
# SEND TELEGRAM
# =========================

def send_telegram(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=data)
    except Exception as e:
        print("TELEGRAM ERROR:", e)

# =========================
# GET KLINES FROM BINANCE
# =========================

def get_klines(symbol):

    url = (
        f"https://api.binance.com/api/v3/klines"
        f"?symbol={symbol}&interval=15m&limit=50"
    )

    response = requests.get(url)

    return response.json()

# =========================
# ANALYZE MARKET
# =========================

def analyze(symbol):

    print(f"ANALYZING {symbol}")

    candles = get_klines(symbol)

    if not candles or isinstance(candles, dict):
        print("ERROR LOADING DATA")
        return

    closes = []

    for candle in candles:
        closes.append(float(candle[4]))

    current_price = closes[-1]

    # EMA
    ema = sum(closes[-20:]) / 20

    # RSI
    gains = []
    losses = []

    for i in range(1, len(closes)):

        diff = closes[i] - closes[i - 1]

        if diff >= 0:
            gains.append(diff)
        else:
            losses.append(abs(diff))

    avg_gain = sum(gains[-14:]) / 14 if gains else 0.01
    avg_loss = sum(losses[-14:]) / 14 if losses else 0.01

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # VOLUME
    volumes = []

    for candle in candles:
        volumes.append(float(candle[5]))

    current_volume = volumes[-1]
    avg_volume = sum(volumes[-20:]) / 20

    volume_spike = current_volume > avg_volume * 1.5
    smart_money = current_volume > avg_volume * 2

    print("PRICE:", current_price)
    print("EMA:", ema)
    print("RSI:", rsi)

    # =========================
    # BUY CONDITIONS
    # =========================

    if (
        current_price > ema
        and rsi > 45
        and volume_spike
    ):

        entry = round(current_price, 4)

        tp = round(current_price * 1.04, 4)

        sl = round(current_price * 0.985, 4)

        message = (
            f"🚀 STRONG BUY SIGNAL\n\n"
            f"PAIR: {symbol}\n\n"
            f"📍 ENTRY: {entry}\n\n"
            f"📊 EMA: {round(ema,4)}\n"
            f"📈 RSI: {round(rsi,2)}\n"
            f"📊 VOLUME SPIKE: {volume_spike}\n"
            f"🐋 SMART MONEY: {smart_money}\n\n"
            f"🎯 TP: {tp}\n"
            f"🛑 SL: {sl}"
        )

        print("SENDING SIGNAL...")

        send_telegram(message)

        print("SIGNAL SENT")

# =========================
# SYMBOLS
# =========================

symbols = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT"
]

# =========================
# START BOT
# =========================

print("BOT STARTED")

send_telegram("🔥 BOT STARTED SUCCESSFULLY")

# =========================
# MAIN LOOP
# =========================

while True:

    try:

        for symbol in symbols:

            analyze(symbol)

            time.sleep(10)

        print("WAITING NEXT SCAN...")

        time.sleep(300)

    except Exception as e:

        print("ERROR:", e)

        send_telegram(f"ERROR: {e}")

        time.sleep(30)
