from class_test import Stock
from openbb_terminal.sdk import openbb
import backtesting
from backtesting import Strategy
from backtesting import Backtest
import datetime


class RSIStrategy(Strategy):

    n1 = 32
    n2 = 73

    start_date = datetime.datetime(2020, 9, 1)
    data = openbb.stocks.load("TSLA", start_date=start_date)
    
    date_for_rsi = start_date - datetime.timedelta(days = 20)

    data_for_rsi = openbb.stocks.load("TSLA", start_date=date_for_rsi)

    
    def RSI():
        close = RSIStrategy.data_for_rsi["Close"]
        rsi = openbb.ta.rsi(close)
        return rsi
    
    def init(self):
        
        self.rsi = self.I(RSIStrategy.RSI)


    def next(self):
        
        if self.rsi < RSIStrategy.n1:
            self.position.close()
            self.buy()

        elif self.rsi > RSIStrategy.n2:
            self.position.close()
            self.sell()

bt = Backtest(RSIStrategy.data, RSIStrategy, cash=10_000, commission=.002)
stats = bt.run()
print(stats)
bt.plot()


""" 
max_value = float('-inf')
for n1 in range(28, 35, 1): 
    for n2 in range(68, 75, 1): 
        RSIStrategy.n1 = n1
        RSIStrategy.n2 = n2
        bt = Backtest(RSIStrategy.data, RSIStrategy, cash=10_000, commission=.002)
        stats = bt.run()
        value = stats["Equity Final [$]"] 
        print(value)
        if value > max_value: 
            max_value = value
            best_n1 = n1
            best_n2 = n2


RSIStrategy.n1 = best_n1
RSIStrategy.n2 = best_n2
bt = Backtest(RSIStrategy.data, RSIStrategy, cash=10_000, commission=.002)
stats = bt.run()
print(stats)

print("Maximum value:", max_value)
print("Best values for n1 and n2:", best_n1, best_n2) """