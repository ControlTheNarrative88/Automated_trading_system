from config import binance_api_key, binance_secret_key
from openbb_terminal.sdk import openbb
from binance import Client
import pandas as pd
import datetime
from supertrend import Supertrend
import time
from class_test import Stock
from backtesting.lib import crossover

client = Client(binance_api_key, binance_secret_key)
class Trade:

    supertrend_status = None
    macd_status = None
    rsi_status = None

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


def supertrend_monitor(ticker):
 
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
            Trade.supertrend_status = True
 
        elif current == previous and current == "Down":
            Trade.supertrend_status = False

        elif previous != current and current == "Upper":
            Trade.supertrend_status = True
            print("changed to Upper")

        elif previous != current and current == "Down":
            Trade.supertrend_status = False
            print("changed to down")
        
        time.sleep(59)      


def macd_monitor(ticker):

    while True:

        df = Trade.get_coin_data(ticker)
        df.rename(columns={'Time': 'date'}, inplace=True)
        df.set_index('date', inplace=True)

        macd_data = Stock.get_macd(for_crypto=True, dataframe = df, chart=True)

        main_line = macd_data['MACD_12_26_9'].values
        signal_line = macd_data['MACDs_12_26_9'].values

        if crossover(main_line, signal_line) and signal_line[0] < 0 and main_line[0] < 0:
            Trade.macd_status = True

        elif crossover(signal_line, main_line) and signal_line[0] > 0 and main_line[0] > 0:
            Trade.macd_status = False
        else: 
            Trade.macd_status = None

        print(Trade.macd_status)
        time.sleep(59)


def rsi_monitor(ticker):

    while True:
            
        df = Trade.get_coin_data(ticker)
        df.rename(columns={'Time': 'date'}, inplace=True)
        df.set_index('date', inplace=True)
        df = df["Close"]

        rsi_data = Stock.get_rsi(for_crypto=True, dataframe = df)

        if rsi_data > float(68):
            Trade.rsi_status = False
        elif rsi_data < float(32):
            Trade.rsi_status = True

        print(Trade.rsi_status, rsi_data)
        time.sleep(59)