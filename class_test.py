from openbb_terminal.sdk import openbb
from nltk.sentiment import SentimentIntensityAnalyzer
from config import fred_key, finnhub_key
import csv

openbb.keys.fred(key = fred_key, persist = True)
openbb.keys.finnhub(key = finnhub_key)

class Stock:


    def load_stock_data(self, return_tail=False):
        data  =  openbb.stocks.load(self, start_date="2020-09-01")
        openbb.forecast.delete(data, "Dividends")
        openbb.forecast.delete(data, "Stock Splits")
        openbb.forecast.delete(data, "Close")
        openbb.forecast.ema(data, target_column = 'Adj Close', period = 50)
        openbb.forecast.ema(data, target_column = 'Adj Close', period = 200)
        openbb.forecast.rsi(data, target_column = 'Adj Close', period = 14)
        if return_tail:
            return data.tail(1)
        return data


    def get_symbol_list_from_index(index_ticker):
        etf = openbb.etf.holdings(index_ticker)
        symbol_list = etf.index.tolist()
        return symbol_list
    
    
    def overbought_or_oversold(self):
        data = Stock.load_stock_data(self, return_tail = True)
        ema200 = data['EMA_200']
        rsi = data['RSI_14_Adj Close']
        curr_price = data["Adj Close"]
        if float(ema200) >= float(curr_price):
            print("EMA 200 Oversold")
        else:
            print("EMA 200 Overbought", ",", ((((curr_price/ema200) - 1) * 100)).item(),"% higher than price")
        if float(rsi) >= 70:
            print ("RSI Overbought", float(rsi))
        elif float(rsi) <= 30:
            print ("RSI Oversold", float(rsi))
        else:
            print(f"RSI === {float(rsi)}")


    def balance_sheet_diff(print_chart = False):

        if print_chart:
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

    @staticmethod
    def get_macd(ticker=None, chart = False, for_crypto = False, dataframe = None):

        if for_crypto:
            data = dataframe["Close"]
            macd_table = openbb.ta.macd(data = data, n_fast = 12, n_slow  = 26, n_signal = 9)
            if chart:
                openbb.ta.macd_chart(data = data, n_fast = 12, n_slow  = 26, n_signal = 9)
            return macd_table
        else:
            data = Stock.load_stock_data(ticker)
            data = data["Adj Close"]
            macd_table = openbb.ta.macd(data = data, n_fast = 12, n_slow  = 26, n_signal = 9)
            if chart:
                openbb.ta.macd_chart(data = data, n_fast = 12, n_slow  = 26, n_signal = 9)
            return macd_table
    
    @staticmethod
    def get_rsi(ticker= None, for_crypto = False, dataframe = None):

        if for_crypto:
            rsi_num = openbb.ta.rsi(data = dataframe, window=14)
            rsi_num = rsi_num['RSI_14'].iloc[-1]
            return rsi_num
        
        df = Stock.load_stock_data(ticker) 
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


    @staticmethod
    def get_spb_ticker_list():

        with open("ListingSecurityList.csv", 'r') as file:
            csv_reader = csv.reader(file, delimiter=';', skipinitialspace=True)
            next(csv_reader) 

            list_of_rows = []
            for row in csv_reader:
                list_of_rows.append(row)

        spb_ticker_list = []
        for elem in range(len(list_of_rows)):
            if list_of_rows[int(elem)][-1] == "Эмитенты с листингом в США":
                spb_ticker_list.append(list_of_rows[elem][1])

        return spb_ticker_list

