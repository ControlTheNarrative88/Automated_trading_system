from openbb_terminal.sdk import openbb
from backtesting import Strategy
from backtesting import Backtest
import pandas as pd



from supertrend import Supertrend

class SupertrendStrategy(Strategy):



    data = openbb.stocks.load("AMD", start_date="2020-09-01")

    Supertrend.supertrend_result_print("AMD", print_plt=False, start_date = "2020-06-01")

    def supertrend_status():
        trend_changes = Supertrend.trend_changes
        df = pd.DataFrame(trend_changes, columns=['Date', 'Previous Trend', 'Current Trend']).drop('Previous Trend', axis=1)
        df = df.reset_index().rename(columns={'Timestamp': 'Date'}).set_index('Date')
        df = df.drop('index', axis=1)
        return df

    @staticmethod
    def extrapotale_status():
        df1 = SupertrendStrategy.data
        df2 = SupertrendStrategy.supertrend_status()

        merged_df = df1.merge(df2, left_index=True, right_index=True, how='left')
        merged_df['Current Trend'] = merged_df['Current Trend'].ffill()
        final_df = pd.DataFrame({'Date': merged_df.index, 'Current Trend': merged_df['Current Trend']})
        final_df = final_df.drop('Date', axis=1)
        return final_df

    def init(self):
        self.supertrend = self.I(SupertrendStrategy.extrapotale_status)



    previous_supertrend = None
    def next(self):


        if self.supertrend == True and SupertrendStrategy.previous_supertrend == False or None:
            if self.position.is_short:
                self.position.close()
            self.buy()

        elif self.supertrend == False and SupertrendStrategy.previous_supertrend == True or None:
            if self.position.is_long:
                self.position.close()
            self.sell()

        SupertrendStrategy.previous_supertrend = self.supertrend


bt = Backtest(SupertrendStrategy.data, SupertrendStrategy, cash=10_000, commission=.002)
stats = bt.run()
print(stats)
bt.plot()


