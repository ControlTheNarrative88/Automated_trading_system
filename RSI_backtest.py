from openbb_terminal.sdk import openbb
from backtesting import Strategy
from backtesting import Backtest
import datetime
import numpy as np



class RSIStrategy(Strategy):

    n1 = 28
    n2 = 68

    tp_value = 1.01
    sl_value = 0.82

    start_date = datetime.datetime(2020, 9, 1)
    data = openbb.stocks.load("SPY", start_date=start_date)
    openbb.forecast.delete(data, "Dividends")
    openbb.forecast.delete(data, "Stock Splits")
    
    date_for_rsi = start_date - datetime.timedelta(days = 20)

    data_for_rsi = openbb.stocks.load("SPY", start_date=date_for_rsi)

    
    def RSI():
        close = RSIStrategy.data_for_rsi["Close"]
        rsi = openbb.ta.rsi(close)
        return rsi
    
    def init(self):
        
        self.rsi = self.I(RSIStrategy.RSI)


    def next(self):

        if self.rsi > RSIStrategy.n2:

            tp_price = (RSIStrategy.data["Close"][-1]) * RSIStrategy.tp_value

            if self.position.is_long:
                self.position.close()

            self.sell(tp= tp_price, limit = tp_price * 1.02)

        if self.rsi < RSIStrategy.n1:

            sl_price = (RSIStrategy.data["Close"][-1]) * RSIStrategy.sl_value 

            if self.position.is_short:
                self.position.close()

            self.buy(sl = sl_price, limit=sl_price*1.02)



# функция очень долгая, но перебирает все варианты значений и стопов, вызывается только один раз
def get_best_values_from_backtest():
    values_list = []
    max_value = float("-inf")
    for tp_value in np.arange(1.01, 1.2, 0.01, dtype=float):
        for sl_value in np.arange(0.8, 0.99, 0.01):
            for n1 in range(28, 35, 1): 
                for n2 in range(68, 75, 1):
                    RSIStrategy.tp_value = tp_value
                    RSIStrategy.sl_value = sl_value
                    RSIStrategy.n1 = n1
                    RSIStrategy.n2 = n2
                    bt = Backtest(RSIStrategy.data, RSIStrategy, cash=10_000, commission=.002)
                    stats = bt.run()
                    value = stats["Equity Final [$]"]
                    print(value)
                    values_list.append(value)
                    if value > max_value: 
                        max_value = value
                        best_tp_value = tp_value
                        best_sl_value = sl_value
                        best_n1 = n1
                        best_n2 = n2

    
    print("Maximum value:", max_value)
    print("Best values for n1 and n2:", best_n1, best_n2)
    print("Best values for tp and sl:", best_tp_value, best_sl_value)

