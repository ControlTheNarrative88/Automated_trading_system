from config import binance_api_key, binance_secret_key
from binance import Client
from openbb_terminal.sdk import openbb
import pandas as pd
import datetime
from supertrend import Supertrend
import matplotlib.pyplot as plt


client = Client(binance_api_key, binance_secret_key)
class Trade:

    def get_coin_data(self, limit=360):

        data = client.get_klines(symbol=self, interval="1m", limit=limit)

        df = pd.DataFrame()

        for candle in range(limit):
            date_time = datetime.datetime.fromtimestamp(data[candle][0] / 1e3)
            high_price = float(data[candle][2])
            low_price = float(data[candle][3])
            close_price = float(data[candle][4])
            new_df = pd.DataFrame({'Time': [date_time], "Close": [close_price],
                                 "High": [high_price],
                                 "Low" : [low_price]
                                  })
            df = pd.concat([df, new_df], ignore_index=True)
        return df
        
    def make_trade(ticker, buy_value, side, type="MARKET"):

        buy_value = buy_value
        df = Trade.get_coin_data(ticker)
        quantity = round(buy_value / df.iloc[-1][ticker])
        trade_status = client.create_order(symbol=ticker, side=side, type=type, quantity= quantity)
        return trade_status


Supertrend.supertrend_result_print(for_crypto=True, dataframe=Trade.get_coin_data("LUNAUSDT"))