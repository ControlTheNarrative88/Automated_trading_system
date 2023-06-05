from config import binance_api_key, binance_secret_key
from binance import Client
from openbb_terminal.sdk import openbb
import pandas as pd
import datetime


client = Client(binance_api_key, binance_secret_key)

def get_coin_data(self, limit=61):

    data = client.get_klines(symbol=self, interval="1m", limit=limit)

    df = pd.DataFrame()

    for candle in range(limit):
        date_time = datetime.datetime.fromtimestamp(data[candle][0] / 1e3)
        close_price = float(data[candle][4])
        new_df = pd.DataFrame({'Time': [date_time], f'{self}': [close_price]})
        df = pd.concat([df, new_df], ignore_index=True)
    return df
    
def make_trade(ticker, buy_value,side, type="MARKET"):

    buy_value = buy_value
    df = get_coin_data(ticker)
    quantity = round(buy_value / df.iloc[-1][ticker])
    trade_status = client.create_order(symbol=ticker, side=side, type=type, quantity= quantity)
    return trade_status


make_trade("LUNAUSDT", 10, "SELL")