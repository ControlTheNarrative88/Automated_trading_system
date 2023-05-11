from openbb_terminal.sdk import openbb
from nltk.sentiment import SentimentIntensityAnalyzer

openbb.keys.fred(key = '07b18df77070f808b8a7976f27910ee4', persist = True)
openbb.keys.finnhub(key = "c2j894iad3ib3m9cept0")


class Stock:


    def load_stock_data(self):
        data  =  openbb.stocks.load(self, start_date="2020-09-01")
        openbb.forecast.delete(data, "Dividends")
        openbb.forecast.delete(data, "Stock Splits")
        openbb.forecast.delete(data, "Close")
        openbb.forecast.ema(data, target_column = 'Adj Close', period = 50)
        openbb.forecast.ema(data, target_column = 'Adj Close', period = 200)
        openbb.forecast.rsi(data, target_column = 'Adj Close', period = 14)
        ## table = data.tail(1)
        return data
    
    
    def overbought_or_oversold(self):
        data = Stock.load_stock_data(self)
        ema200 = data['EMA_200']
        rsi = data['RSI_14_Adj Close']
        curr_price = data["Adj Close"]
        if float(ema200) >= float(curr_price):
            print("EMA 200 Oversold")
        else:
            print("EMA 200 Overbought")
        if float(rsi) >= 70:
            print ("RSI Overbought", float(rsi))
        elif float(rsi) <= 30:
            print ("RSI Oversold", float(rsi))
        else:
            print(f"RSI === {float(rsi)}")


    def balance_sheet_diff():

        openbb.economy.fred_chart(series_ids=["WALCL"], start_date="2020-05-01")
        fed_balance = openbb.economy.fred(series_ids=["WALCL"], start_date="2020-05-01")
        df = fed_balance[-2]

        now = df.iloc[-1]['WALCL']
        last_week = df.iloc[-2]['WALCL']
        two_weeks_ago = df.iloc[-3]['WALCL']
        three_weeks_ago = df.iloc[-4]['WALCL']


        def perc_calc(base, now):
            if now >= base:
                return ((now / base) * 100) - 100
            return (((base - now) / now) * 100)*-1

        
        return perc_calc(last_week,now), perc_calc(two_weeks_ago, now), perc_calc(three_weeks_ago,now)


    def get_ema(self):
        data = Stock.load_stock_data(self)
        data = data["Adj Close"]
        ema  = openbb.ta.ema(data)
        return ema

    def get_macd(self):

        data = Stock.load_stock_data(self)
        data = data["Adj Close"]
        macd_table = openbb.ta.macd(data = data, n_fast = 12, n_slow  = 26, n_signal = 9)
        macd_chart = openbb.ta.macd_chart(data = data, n_fast = 12, n_slow  = 26, n_signal = 9)
        return macd_table.tail(5), macd_chart
    
    def get_rsi(self):
        df = Stock.load_stock_data(self) 
        df = df["Adj Close"]
        rsi_num = openbb.ta.rsi(data = df, window = 14)
        rsi_num = rsi_num['RSI_14'].iloc[-1]
        return rsi_num

    def get_bbands(self, chart = False):
        data = Stock.load_stock_data(self)
        if chart:
            openbb.ta.bbands_chart(data)
        bband = openbb.ta.bbands(data)
        return bband
    
    def get_news_sentiment(self):
        
        openbb.stocks.ba.snews_chart(self)

        news = openbb.stocks.ba.cnews(self)
        list_of_news = []
        for i in range(15):
            summary = news[i]["summary"]
            list_of_news.append(summary)

        filtered_news = [h for h in list_of_news if not h.startswith("Looking for")]

        for i in filtered_news:
            sia = SentimentIntensityAnalyzer()
            sentiment_score = sia.polarity_scores(i)
            print(i)
            print(sentiment_score)

        openbb.stocks.ba.headlines_chart(self)
        print(openbb.stocks.ba.headlines(self))

    def build_rnn_forecast(self):
        df = Stock.load_stock_data(self)
        openbb.forecast.rnn_chart(data = df, target_column="Adj Close", n_predict = 5)

    def build_brnn_forecast(self):
        df = Stock.load_stock_data(self)
        openbb.forecast.brnn_chart(data = df, target_column="Adj Close", n_predict = 5)
