import pandas as pd
import numpy as np
import requests
from collections import Counter
from settings import SECRET_KEY, APP_HASH, API_ID, BOT_NAME, ROOM_ID
from telethon import TelegramClient, events

client = TelegramClient(BOT_NAME, API_ID, APP_HASH)

ENDPOINT = "https://query1.finance.yahoo.com/v8/finance/chart/"

# Stock symbol


def createURL(sym, ran, inter):
    return ENDPOINT+sym+"?"+"range="+ran+"&interval="+inter


def sendMessage(_token, _id, _message):
    url = 'https://api.telegram.org/bot'+_token + \
        '/sendMessage?chat_id='+_id+'&text='+_message
    res = requests.post(url)
    return res


url = createURL("BTC-USD", "1d", "2m")
req = requests.get(url).json()
_rawcolumn_names = list(req['chart']['result'][0])
values = req['chart']['result'][0][_rawcolumn_names[2]]['quote'][0]
cols = list(values.keys())

# Create Dataframe
df = pd.DataFrame(columns=cols)
df[cols[0]] = values['close']
df[cols[1]] = values['high']
df[cols[2]] = values['open']
df[cols[3]] = values['volume']
df[cols[4]] = values['low']

sma_5 = pd.DataFrame()
sma_5['Close Price'] = df['close'].rolling(window=5).mean().dropna()
sma_8 = pd.DataFrame()
sma_8['Close Price'] = df['close'].rolling(window=8).mean().dropna()
sma_13 = pd.DataFrame()
sma_13['Close Price'] = df['close'].rolling(window=13).mean().dropna()

data = pd.DataFrame()
data['BTC-USD'] = df['close']
data['SMA 5'] = sma_5['Close Price']
data['SMA 8'] = sma_8['Close Price']
data['SMA 13'] = sma_13['Close Price']


def create_signal(data):
    buy_sig_price = []
    sell_sig_price = []
    flag = -1

    for i in range(len(data)):
        if data['SMA 5'][i] > data['SMA 8'][i]:
            if flag != 1:

                buy_sig_price.append(data["BTC-USD"][i])
                sell_sig_price.append(np.nan)
                flag = 1
            else:
                buy_sig_price.append(np.nan)
                sell_sig_price.append(np.nan)

        elif data['SMA 5'][i] < data['SMA 8'][i]:
            if flag != 0:
                buy_sig_price.append(np.nan)
                sell_sig_price.append(data["BTC-USD"][i])
                flag = 0
            else:
                buy_sig_price.append(np.nan)
                sell_sig_price.append(np.nan)

        elif data['SMA 8'][i] > data['SMA 13'][i]:
            if flag != 1:
                buy_sig_price.append(data["BTC-USD"][i])
                sell_sig_price.append(np.nan)
                flag = 1

            else:

                buy_sig_price.append(np.nan)
                sell_sig_price.append(np.nan)
        elif data['SMA 8'][i] < data['SMA 13'][i]:
            if flag != 0:
                buy_sig_price.append(np.nan)
                sell_sig_price.append(data["BTC-USD"][i])
                flag = 0

            else:

                buy_sig_price.append(np.nan)
                sell_sig_price.append(np.nan)
        elif data['SMA 5'][i] > data['SMA 13'][i]:
            if flag != 1:
                buy_sig_price.append(data["BTC-USD"][i])
                sell_sig_price.append(np.nan)
                flag = 1

            else:

                buy_sig_price.append(np.nan)
                sell_sig_price.append(np.nan)
        elif data['SMA 5'][i] < data['SMA 13'][i]:
            if flag != 0:
                buy_sig_price.append(np.nan)
                sell_sig_price.append(data["BTC-USD"][i])
                flag = 0

            else:

                buy_sig_price.append(np.nan)
                sell_sig_price.append(np.nan)

        else:

            buy_sig_price.append(np.nan)
            sell_sig_price.append(np.nan)

    return (buy_sig_price, sell_sig_price)


# Storing values into a variable

buy_sell = create_signal(data)
data["Buy Signal Price"] = buy_sell[0]
data["Sell Signal Price"] = buy_sell[1]
buy_price = data["Buy Signal Price"].dropna().values.astype(float)
sell_price = data["Sell Signal Price"].dropna().values.astype(float)


def validateBS():
    arr = []

    for i in range(0, 23):
        if buy_price[i] < sell_price[i]:
            arr.append(1)
        else:
            arr.append(0)

    return arr


def results():
    arr = validateBS()
    if arr.count(True) < arr.count(False):
        msg = "Sell"
    else:
        msg = "Buy"

    return msg


# results()
@client.on(events.NewMessage(chats=("testSite")))
async def handle_signal_req(event):
    # await event.reply(sendMessage(SECRET_KEY, ROOM_ID, results()))
    if 'signal' in event.raw_text or 'Signal' in event.raw_text or 'SIGNAL' in event.raw_text:
        await event.reply(sendMessage(SECRET_KEY, ROOM_ID, results()))


@client.on(events.NewMessage(chats=("testSite")))
async def handle_price_req(event):
    price = str(data['BTC-USD'].tail(1).dropna().values.astype(float)[0])
    if 'price' in event.raw_text or 'Price' in event.raw_text or 'PRICE' in event.raw_text:
        await event.reply(sendMessage(
            SECRET_KEY,
            ROOM_ID,
            price
        ))

client.start()
client.run_until_disconnected()
