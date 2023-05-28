from openbb_terminal.sdk import openbb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from class_test import Stock

def supertrend(df, atr_period, multiplier):
    
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    # calculate ATR
    price_diffs = [high - low, 
                   high - close.shift(), 
                   close.shift() - low]

    true_range = pd.concat(price_diffs, axis=1)
    true_range = true_range.abs().max(axis=1)
    # default ATR calculation in supertrend indicator
    atr = true_range.ewm(alpha=1/atr_period,min_periods=atr_period).mean() 
    # df['atr'] = df['tr'].rolling(atr_period).mean()
    
    # HL2 is simply the average of high and low prices
    hl2 = (high + low) / 2
    # upperband and lowerband calculation
    # notice that final bands are set to be equal to the respective bands
    final_upperband = upperband = hl2 + (multiplier * atr)
    final_lowerband = lowerband = hl2 - (multiplier * atr)
    
    # initialize Supertrend column to True
    supertrend = [True] * len(df)

        
    for i in range(1, len(df.index)):
        curr, prev = i, i-1
        
        # if current close price crosses above upperband
        if close[curr] > final_upperband[prev]:
            supertrend[curr] = True
        # if current close price crosses below lowerband
        elif close[curr] < final_lowerband[prev]:
            supertrend[curr] = False
        # else, the trend continues
        else:
            supertrend[curr] = supertrend[prev]
            
            # adjustment to the final bands
            if supertrend[curr] == True and final_lowerband[curr] < final_lowerband[prev]:
                final_lowerband[curr] = final_lowerband[prev]
            if supertrend[curr] == False and final_upperband[curr] > final_upperband[prev]:
                final_upperband[curr] = final_upperband[prev]

        # to remove bands according to the trend direction
        if supertrend[curr] == True:
            final_upperband[curr] = np.nan
        else:
            final_lowerband[curr] = np.nan
    
        if supertrend[curr] != supertrend[prev]:
            trend_change = (df.index[curr], supertrend[prev], supertrend[curr])
            trend_changes.append(trend_change)

    return pd.DataFrame({
        'Supertrend': supertrend,
        'Final Lowerband': final_lowerband,
        'Final Upperband': final_upperband
    }, index=df.index)
    

trend_changes = []

atr_period = 10
atr_multiplier = 3.0

def supertrend_result_print(ticker):


    df = openbb.stocks.load(ticker, start_date = "2022-09-01")

    supertrend_result = supertrend(df, atr_period, atr_multiplier)
    df = df.join(supertrend_result)

    plt.plot(df['Close'], label='Close Price')
    plt.plot(df['Final Lowerband'], 'g', label = 'Final Lowerband')
    plt.plot(df['Final Upperband'], 'r', label = 'Final Upperband')
    plt.legend()
    plt.show()


    previous_trend_label = "Upper"
    current_trend_label = "Down"

    for change in trend_changes:
        previous_trend = previous_trend_label if change[1] else current_trend_label
        current_trend = previous_trend_label if change[2] else current_trend_label
        print(f"Date: {change[0]}, Previous Trend: {previous_trend}, Current Trend: {current_trend}")


def iterate_throught_sbp_list():

    spb_stock_list = Stock.get_spb_ticker_list()
    spb_stock_list = spb_stock_list[:100]


    supertrend_stocks = []

    for symbol in spb_stock_list:
        df = openbb.stocks.load(symbol, start_date='2023-01-01')
        if len(df) == 0: continue
        supertrend_df = supertrend(df, atr_period, atr_multiplier)
        if not supertrend_df['Supertrend'][-2] and supertrend_df['Supertrend'][-1]:
            supertrend_stocks.append(symbol)

    return supertrend_stocks

list = iterate_throught_sbp_list()

for stock in list:
    supertrend_result_print(stock)