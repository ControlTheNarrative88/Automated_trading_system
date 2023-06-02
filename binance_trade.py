from config import binance_api_key, binance_secret_key
from binance import Client
from openbb_terminal.sdk import openbb
import pandas as pd

client = Client(binance_api_key, binance_secret_key)

class Coin:
    def get_coin_data(self, limit=61):
        # интервал обновления данных по цене можно менять, в данном случае раз в минуту
        data = client.get_klines(symbol=self, interval="1m", limit=limit)

        df = pd.DataFrame()

        # упаковываем в датафрейм для облегчения дальнейшей работы
        for candle in range(limit):
            date_time = datetime.datetime.fromtimestamp(data[candle][0] / 1e3)
            close_price = float(data[candle][4])
            new_df = pd.DataFrame({'Time': [date_time], f'{self}': [close_price]})
            df = pd.concat([df, new_df], ignore_index=True)
        return df