import requests
import pandas as pd
from discord.ext import tasks, commands

bot = commands.Bot(command_prefix='!')

def fetch_price_data():
    url = "https://api.bybit.com/v2/public/kline/list" #imaginary API key
    params = {
        "symbol": "SOLUSDT",
        "interval": "60",  # 1-hour interval for data
        "from": int(time.time()) - 60 * 60 * 24,  # Data from the last 24 hours
    }
    response = requests.get(url, params=params)
    data = response.json()
    return pd.DataFrame(data['result'])

def calculate_rsi(df, periods=14):
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

@tasks.loop(minutes=60)
async def check_rsi():
    df = fetch_price_data()
    df['rsi'] = calculate_rsi(df)
    last_rsi = df['rsi'].iloc[-1]

    if last_rsi > 70:
        await alert_channel.send("Attention: RSI for SOL/USDT has exceeded 70! Possible overbought.")
    elif last_rsi < 30:
        await alert_channel.send("Attention: RSI for SOL/USDT has fallen below 30! Possible oversold.")

@bot.event
async def on_ready():
    global alert_channel
    alert_channel = bot.get_channel(CHANNEL_DISCORD_ID)  
    check_rsi.start()

bot.run('Discord_token_here')