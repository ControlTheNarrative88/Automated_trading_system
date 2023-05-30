from openbb_terminal.sdk import openbb
from backtesting import Strategy
from backtesting import Backtest
import datetime
import pandas as pd
import numpy as np

from supertrend import Supertrend

class SupertrendStrategy(Strategy):

    data = openbb.stocks.load("SPY", start_date="2020-09-01")

    Supertrend.supertrend_result_print("SPY", print_plt=False)

    def supertrend_status():
        trend_changes = Supertrend.trend_changes
        df = pd.DataFrame(trend_changes, columns=['Date', 'Previous Trend', 'Current Trend']).drop('Previous Trend', axis=1)
        df = df.reset_index().rename(columns={'Timestamp': 'Date'}).set_index('Date')
        df = df.drop('index', axis=1)
        return df

    def extrapotale_status():
        df1 = SupertrendStrategy.data
        df2 = SupertrendStrategy.supertrend_status()

        merged_df = df1.merge(df2, left_index=True, right_index=True, how='left')
        merged_df['Current Trend'] = merged_df['Current Trend'].ffill()
        final_df = pd.DataFrame({'Date': merged_df.index, 'Current Trend': merged_df['Current Trend']})
        final_df = final_df.drop('Date', axis=1)
        return final_df

    @staticmethod
    def is_value(df, date):
        if date in df.index:
            value = df.loc[date, 'Current Trend']
            return True
        else:
            return False

    def init(self):
        # Initialize variables
        self.supertrend = self.I(SupertrendStrategy.supertrend_status)

    def next(self):
        if self.supertrend == True:
            self.buy()
        elif self.supertrend == False:
            self.sell()

""" 
bt = Backtest(SupertrendStrategy.data, SupertrendStrategy, cash=10_000, commission=.002)
stats = bt.run()
print(stats)
bt.plot()
 """