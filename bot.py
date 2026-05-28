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
# GET SPOT SYMBOLS
# =========================

def get_spot_symbols():

    try:

        url = "https://api.binance.com/api/v3/exchangeInfo"

        response = requests.get(url, timeout=10)

        data = response.json()

        # لو Binance رجع Error
        if "symbols" not in data:

            print("BINANCE ERROR:", data)

            return [
                "BTCUSDT",
                "ETHUSDT",
                "SOLUSDT",
                "BNBUSDT",
                "XRPUSDT"
            ]

        symbols = []

        for s in data["symbols"]:

            try:

                if (
                    s["quoteAsset"] == "USDT"
                    and s["status"] == "TRADING"
                    and s["isSpotTradingAllowed"]
                ):

                    symbol = s["symbol"]

                    # فلترة العملات الغريبة
                    if (
                        "UP" not in symbol
                        and "DOWN" not in symbol
                        and "BULL" not in symbol
                        and "BEAR" not in symbol
                    ):

                        symbols.append(symbol)

            except:
                pass

        return symbols

    except Exception as e:

        print("GET SYMBOLS ERROR:", e)

        return [
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
            "BNBUSDT",
            "XRPUSDT"
        ]

# =========================
# GET KLINES
# =========================

def get_klines(symbol):

    try:

        url = (
            f"https://api.binance.com/api/v3/klines"
            f"?symbol={symbol}&interval=15m&limit=50"
        )

        response = requests.get(url, timeout=10)

        return response.json()

    except Exception as e:

        print(f"KLINES ERROR {symbol}: {e}")

        return None

# =========================
# ANALYZE MARKET
# =========================

def analyze(symbol):

    print(f"ANALYZING {symbol}")

    candles = get_klines(symbol)

    if not candles:
        return

    if isinstance(candles, dict):
        return

    closes = []

    for candle in candles:

        closes.append(float(candle[4]))

    current_price = closes[-1]

    # =========================
    # EMA
    # =========================

    ema = sum(closes[-20:]) / 20

    # =========================
    # RSI
    # =========================

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

    # =========================
    # VOLUME
    # =========================

    volumes = []

    for candle in candles:

        volumes.append(float(candle[5]))

    current_volume = volumes[-1]

    avg_volume = sum(volumes[-20:]) / 20

    volume_spike = current_volume > avg_volume * 1.3

    smart_money = current_volume > avg_volume * 2

    print("PRICE:", current_price)
    print("EMA:", round(ema, 6))
    print("RSI:", round(rsi, 2))

    # =========================
    # BUY CONDITIONS
    # =========================

    if (
        current_price > ema
        and rsi > 40
    ):

        entry = round(current_price, 6)

        tp = round(current_price * 1.04, 6)

        sl = round(current_price * 0.985, 6)

        message = (
            f"🚀 STRONG BUY SIGNAL\n\n"
            f"PAIR: {symbol}\n\n"
            f"📍 ENTRY: {entry}\n\n"
            f"📊 EMA: {round(ema,6)}\n"
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
# START BOT
# =========================

print("🚀 BOT STARTED")

send_telegram("🔥 BOT STARTED SUCCESSFULLY")

# =========================
# LOAD SYMBOLS
# =========================

symbols = get_spot_symbols()

print(f"TOTAL SYMBOLS: {len(symbols)}")

# =========================
# MAIN LOOP
# =========================

while True:

    try:

        for symbol in symbols:

            try:

                analyze(symbol)

                time.sleep(3)

            except Exception as e:

                print(f"ERROR ANALYZING {symbol}: {e}")

        print("WAITING NEXT SCAN...")

        # كل 5 دقائق
        time.sleep(300)

    except Exception as e:

        print("MAIN ERROR:", e)

        send_telegram(f"MAIN ERROR: {e}")

        time.sleep(30)
