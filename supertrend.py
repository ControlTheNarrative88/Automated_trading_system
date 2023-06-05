from openbb_terminal.sdk import openbb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from class_test import Stock


class Supertrend:

    trend_changes = []
    atr_period = 10
    atr_multiplier = 3
    start_date = "2020-06-01"
    bands = pd.DataFrame()

    def supertrend(df, atr_period=10, multiplier=3):

        trend_changes = []

        
        high = df['High']
        low = df['Low']
        close = df['Close']
        
        # расчет ATR
        price_diffs = [high - low, 
                    high - close.shift(), 
                    close.shift() - low]

        true_range = pd.concat(price_diffs, axis=1)
        true_range = true_range.abs().max(axis=1)
        atr = true_range.ewm(alpha=1/atr_period,min_periods=atr_period).mean() 
        
        # средняя между самой высокой и низкой ценой
        hl2 = (high + low) / 2

        Supertrend.bands["Upperband"] = final_upperband  = hl2 + (multiplier * atr)
        Supertrend.bands["Lowerband"] = final_lowerband  = hl2 - (multiplier * atr)
        
        supertrend = [True] * len(df)
            
        for i in range(1, len(df.index)):
            curr, prev = i, i-1
            
            # если текущая цена пересекает скользящую снизу
            if close[curr] > final_upperband[prev]:
                supertrend[curr] = True
            # если текущая цена пересекает скользящую сверху
            elif close[curr] < final_lowerband[prev]:
                supertrend[curr] = False
            else:
                supertrend[curr] = supertrend[prev]
                

                if supertrend[curr] == True and final_lowerband[curr] < final_lowerband[prev]:
                    final_lowerband[curr] = final_lowerband[prev]
                if supertrend[curr] == False and final_upperband[curr] > final_upperband[prev]:
                    final_upperband[curr] = final_upperband[prev]

            if supertrend[curr] == True:
                final_upperband[curr] = np.nan
            else:
                final_lowerband[curr] = np.nan

            trend_change = (df.index[curr], supertrend[prev], supertrend[curr])
            trend_changes.append(trend_change)

            Supertrend.trend_changes = trend_changes
            
        return pd.DataFrame({
            'Supertrend': supertrend,
            'Final Lowerband': final_lowerband,
            'Final Upperband': final_upperband
        }, index=df.index)
        

    def supertrend_result_print(ticker=None, print_plt=True, start_date = "2020-08-29", for_crypto=False, dataframe = None):

        if for_crypto:
            supertrend_result = Supertrend.supertrend(dataframe, atr_period=10, multiplier=3)
            dataframe = dataframe.join(supertrend_result)
            dataframe.set_index('Time', inplace=True)
            dataframe.index = dataframe.index.strftime('%H:%M')
        else:   
            dataframe = openbb.stocks.load(ticker, start_date = start_date)
            supertrend_result = Supertrend.supertrend(dataframe, Supertrend.atr_period, Supertrend.atr_multiplier)
            dataframe = dataframe.join(supertrend_result)

        # построение графика
        if print_plt:
            plt.plot(dataframe['Close'], label='Close Price')
            plt.plot(dataframe['Final Lowerband'], 'g', label = 'Final Lowerband')
            plt.plot(dataframe['Final Upperband'], 'r', label = 'Final Upperband')
            plt.legend()
            plt.show()


        previous_trend_label = "Upper"
        current_trend_label = "Down"

        trend_changes = []
        
        #список изменений супертренда
        for change in Supertrend.trend_changes:
            previous_trend = previous_trend_label if change[1] else current_trend_label
            current_trend = previous_trend_label if change[2] else current_trend_label
            trend_changes.append((change[0], f'Previous trend: {previous_trend}', f'Current trend: {current_trend}'))
    
        return trend_changes


    # перебор всех акций имитентов с регистрацией в США, поиск тех, которые недавно начали  свой супертренд
    def iterate_through_sbp_list():

        spb_stock_list = Stock.get_spb_ticker_list()
        spb_stock_list = spb_stock_list[:50]

        supertrend_stocks = []
        for symbol in spb_stock_list:
            df = openbb.stocks.load(symbol, start_date=Supertrend.start_date)
            if len(df) == 0:
                continue
            supertrend_df = Supertrend.supertrend(df, Supertrend.atr_period, Supertrend.atr_multiplier)
            if not supertrend_df['Supertrend'][-2] and supertrend_df['Supertrend'][-1]:
                supertrend_stocks.append(symbol)

        return supertrend_stocks
