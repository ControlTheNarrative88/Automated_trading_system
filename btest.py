import backtesting
from backtesting import Strategy
from backtesting import Backtest
from backtesting.lib import crossover
from openbb_terminal.sdk import openbb
from class_test import Stock
import pandas as pd

data = openbb.stocks.load("SPY", start_date = "2020-09-01")

def SMA(self):
    return pd.Series(values).rolling(n).mean()

def RSI(self):
    Stock.get_rsi(self)

def MACD(self):
    Stock.get_macd(self)

def BollingerBands(self):
    Stock.get_bbands(self)

class SmaCross(Strategy):
    # Define the two MA lags as *class variables*
    # for later optimization
    n1 = 50
    n2 = 200
    
    def init(self):
        # Precompute the two moving averages
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)
        
        # Get RSI
        self.rsi = self.I(RSI, self.data.Close)
        
        # Get MACD
        macd_table, macd_chart = self.data.get_macd()
        self.macd = self.I(MACD, macd_table["macd"], macd_table["macdsignal"], macd_chart["hist"])
        
        # Get Bollinger Bands
        self.bband = self.I(BollingerBands, self.data.Close)

    
    def next(self):
        if (self.sma1[-2] < self.sma2[-2] and
                self.sma1[-1] > self.sma2[-1] and
                self.rsi[-1] < 30 and
                self.macd.macd[-1] > self.macd.macdsignal[-1] and
                self.bband.position[-1] == 1):
            self.position.close()
            self.buy()

        elif (self.sma1[-2] > self.sma2[-2] and    # Ugh!
              self.sma1[-1] < self.sma2[-1] and
              self.rsi[-1] > 70 and
              self.macd.macd[-1] < self.macd.macdsignal[-1] and
              self.bband.position[-1] == -1):
            self.position.close()
            self.sell()

        # Else, if sma1 crosses below sma2, close any existing
        # long trades, and sell the asset
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()

bt = Backtest(data, SmaCross, cash=10_000, commission=.002)
stats = bt.optimize(n1=range(5, 30, 5),
                    n2=range(10, 70, 5),
                    maximize='Equity Final [$]',
                    constraint=lambda param: param.n1 < param.n2)
print(stats)
bt.plot()