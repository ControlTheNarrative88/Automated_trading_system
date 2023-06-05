from config import binance_api_key, binance_secret_key
from binance import Client
import pandas as pd
import datetime
from supertrend import Supertrend
import time
import numpy as np

client = Client(binance_api_key, binance_secret_key)
class Trade:

    status = None

    def get_coin_data(self, limit=60):

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
        
    def make_trade(ticker, buy_volume, side, type="MARKET"):

        buy_volume = buy_volume
        df = Trade.get_coin_data(ticker)
        quantity = round(buy_volume / df.iloc[-1][ticker])
        trade_status = client.create_order(symbol=ticker, side=side, type=type, quantity= quantity)
        return trade_status


def foo(ticker):
 
    while True:
        
        Supertrend.supertrend_result_print(for_crypto=True, dataframe=Trade.get_coin_data(ticker))
        dataframe = Trade.get_coin_data(ticker)
        price = dataframe.tail(1)["Close"].values[0]
        candle_time = dataframe.tail(1)["Time"].values[0]
        trend_changes = Supertrend.supertrend_result_print(for_crypto=True, dataframe=Trade.get_coin_data(ticker), print_plt=False)
        previous = trend_changes[-1][1].split()[2]
        current = trend_changes[-1][2].split()[2]
        print(f'Previous trend: {previous}')
        print(f'Current trend: {current}, {candle_time}, {price}')


        if current == previous and current == "Upper":
            Trade.status = True
 
        elif current == previous and current == "Down":
            Trade.status = False

        elif previous != current and current == "Upper":
            Trade.status = True
            print("changed to Upper")

        elif previous != current and current == "Down":
            Trade.status = False
            print("changed to down")
        
        time.sleep(59)      
