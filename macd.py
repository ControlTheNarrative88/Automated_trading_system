from class_test import Stock
from openbb_terminal.sdk import openbb
from backtesting import Strategy
from backtesting import Backtest
import datetime
from backtesting.lib import crossover

class MacdStrategy(Strategy):

    start_date = datetime.datetime(2020, 9, 1)

    data = openbb.stocks.load("AMD", start_date=start_date)
    openbb.forecast.delete(data, "Dividends")
    openbb.forecast.delete(data, "Stock Splits")

    date_for_macd = start_date - datetime.timedelta(days = 47)

    data_for_macd = openbb.stocks.load("AMD", start_date=date_for_macd)

    data_for_macd = data_for_macd["Close"]



    def macd_main_line():
        
        macd_data = openbb.ta.macd(MacdStrategy.data_for_macd)

        main_line = macd_data['MACD_12_26_9'].values

        return main_line
    
    
    def macd_signal_line():

        macd_data = openbb.ta.macd(MacdStrategy.data_for_macd)

        signal_line = macd_data['MACDs_12_26_9'].values
 
        return signal_line
    
    
    def init(self):

        self.macd_main = self.I(MacdStrategy.macd_main_line)

        self.macd_signal = self.I(MacdStrategy.macd_signal_line)


    def next(self):
        
        price = self.data.Close[-1]
        print(price)
            
        if crossover(self.macd_main, self.macd_signal) and self.macd_signal < 0 and self.macd_main < 0:
        
            if self.position.is_short:
                self.position.close()

            
            self.buy()

        if crossover(self.macd_signal, self.macd_main) and self.macd_signal > 0 and self.macd_main > 0:
        
            if self.position.is_long:
                self.position.close()

            self.sell()



bt = Backtest(MacdStrategy.data, MacdStrategy, cash=10_000, commission=.002)
stats = bt.run()
print(stats)
#bt.plot()

нихуя не работает сл и тп