from binance.client import Client
import requests
import time

# =========================
# CONFIG
# =========================

API_KEY = "vfaCeckzusrSoZHjL3v0r5ixi4zG8AG2yX3atfJAzpQf1QeKfFzAV8XRDu0EBTID"
API_SECRET = "4MxCLa2SuSfeaVBaxpYJB818iVeQJTsQBpxiACAhWHRa0pVxsjiaThtn3wX3xkuz"

TOKEN = "8871701058:AAEdXKgLcJGznFY4NA-Rc2WoqgKsjvUsYkY"
CHAT_ID = "6384233386"

client = Client(API_KEY, API_SECRET)

# =========================
# TELEGRAM
# =========================

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })

# =========================
# GET SPOT SYMBOLS (FILTERED)
# =========================

def get_spot_symbols():
    exchange_info = client.get_exchange_info()
    tickers = client.get_ticker()

    volume_map = {t['symbol']: float(t['quoteVolume']) for t in tickers}

    symbols = []

    for s in exchange_info['symbols']:
        if (
            s['status'] == 'TRADING' and
            s['quoteAsset'] == 'USDT' and
            s['isSpotTradingAllowed']
        ):
            if volume_map.get(s['symbol'], 0) > 1000000:
                symbols.append(s['symbol'])

    return symbols

# =========================
# COOLDOWN SYSTEM
# =========================

last_signal_time = {}
COOLDOWN = 3600

# =========================
# ANALYZE MARKET
# =========================

def analyze(symbol):

    candles = client.get_klines(
        symbol=symbol,
        interval="15m",
        limit=50
    )

    closes = []
    volumes = []

    for c in candles:
        closes.append(float(c[4]))
        volumes.append(float(c[5]))

    entry = closes[-1]

    # =========================
    # INDICATORS
    # =========================

    ema = sum(closes[-20:]) / 20

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

    current_volume = volumes[-1]
    avg_volume = sum(volumes[-20:]) / 20

    volume_spike = current_volume > avg_volume * 1.5
    smart_money = current_volume > avg_volume * 2

    # =========================
    # STRONG SIGNAL FILTER
    # =========================

    if (
        entry > ema and
        rsi < 70 and
        volume_spike and
        smart_money
    ):

        # cooldown
        now = time.time()

        if symbol in last_signal_time:
            if now - last_signal_time[symbol] < COOLDOWN:
                return

        last_signal_time[symbol] = now

        # =========================
        # SMART TP / SL FIX
        # =========================

        # dynamic precision (important fix)
        if entry < 1:
            tp = entry * 1.05
            sl = entry * 0.98
        else:
            tp = entry * 1.03
            sl = entry * 0.985

        entry_low = entry * 0.998
        entry_high = entry * 1.002

        # =========================
        # MESSAGE
        # =========================

        message = (
            f"🚀 STRONG BUY SIGNAL\n\n"
            f"PAIR: {symbol}\n\n"
            f"📍 ENTRY ZONE: {round(entry_low,6)} - {round(entry_high,6)}\n"
            f"📌 ENTRY: {round(entry,6)}\n\n"
            f"📊 EMA: {round(ema,6)}\n"
            f"📈 RSI: {round(rsi,2)}\n"
            f"📊 VOLUME SPIKE: {volume_spike}\n"
            f"🐋 SMART MONEY: {smart_money}\n\n"
            f"🎯 TP: {round(tp,6)}\n"
            f"🛑 SL: {round(sl,6)}\n"
        )

        print(f"SIGNAL SENT: {symbol}")
        send_telegram(message)

# =========================
# START BOT
# =========================

print("🚀 BOT STARTED")

send_telegram("🔥 SMART TRADING BOT STARTED")

symbols = get_spot_symbols()

print("TOTAL SYMBOLS:", len(symbols))

# =========================
# MAIN LOOP
# =========================

while True:
    try:
        for symbol in symbols:
            analyze(symbol)
            time.sleep(1.2)

        print("WAITING NEXT CYCLE...")
        time.sleep(30)

    except Exception as e:
        print("ERROR:", e)
        send_telegram(f"ERROR: {e}")
        time.sleep(10)
