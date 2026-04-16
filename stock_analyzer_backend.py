#!/usr/bin/env python
# coding: utf-8

# In[24]:


import yfinance as yf
from pprint import pprint
import numpy as np
import pandas as pd

class StockAnalyzer:
    def __init__(self, ticker_symbol, start, end):
        self.ticker_symbol = ticker_symbol #initializing with itself -- remember later 
        self.ticker = yf.Ticker(ticker_symbol) 
        self.data = self.ticker.history(start=start, end=end)
        self.start = start
        self.end = end

    def average_price(self):
        closing_data = self.data['Close']
        opening_data = self.data['Open']
        day_high = self.data['High']
        day_low = self.data['Low']
        self.avg = round(((closing_data + opening_data + day_low + day_high)/4), 2)
        self.max_avg = self.avg.max()
        self.min_avg = self.avg.min()
        #std calculated based off of official settled price for the day
        self.std_close = self.data['Close'].std()
        self.range = round((self.max_avg - self.min_avg), 2)
        self.max_date = self.avg.idxmax()
        self.min_date = self.avg.idxmin()
        self.cv = round((self.std_close / self.data['Close'].mean()) * 100, 2)
        self.stock_return = (closing_data.iloc[-1] - closing_data.iloc[0]) / closing_data.iloc[0] * 100
        rolling_max = closing_data.cummax()
        drawdown = (closing_data - rolling_max) / rolling_max * 100
        self.max_drawdown = drawdown.min()

    def print_important_info(self):
        print(f"The day with the highest average price was {self.max_date.date()} at ${self.max_avg}.")
        print(f"The day with the lowest average price was {self.min_date.date()} at ${self.min_avg}")
        print(f"The stock's price ranged about ${self.range} over this period")
        if self.cv < 10:
            print(f"The stock was relatively stable at {self.cv}%")
        elif self.cv < 20:  
            print(f"Your stock was moderately volatile at {self.cv}%")
        else:
            print(f"Your stock was relatively volatile at {self.cv}%")
        print(f"The maximum amount of {self.ticker_symbol} was {self.max_drawdown:.2f}%")




class Portfolio:
    def __init__(self, stocks, weights):
        self.stocks = stocks
        self.weights = weights 
        self.SP = yf.Ticker("^GSPC")
        self.start = self.stocks[0].start 
        self.end = self.stocks[0].end
        self.sp_data = self.SP.history (start=self.start, end=self.end)
        #pulling risk-free nominal from YF db
        self.RF = yf.Ticker("^IRX")
        self.rf_data = self.RF.history (start=self.start, end=self.end)
        if round(sum(self.weights), 2) != 1.0:
            raise ValueError("Weights must add up to 1.0!")


    def calculations(self):
        #closing price for first day
       sp_end_data1 = self.sp_data["Close"].iloc[0]
       #closing price for the last day
       sp_end_data2 = self.sp_data['Close'].iloc[-1]
       self.sp_return = (sp_end_data2 - sp_end_data1)/sp_end_data1 * 100
       #each seperate running total for stocks can subtracted/added to each other 
       self.portfolio_return = 0 
       for stock, weight in zip(self.stocks, self.weights):
           self.portfolio_return += weight * stock.stock_return
       self.alpha = self.portfolio_return  - self.sp_return       
       self.rf_rate = self.rf_data["Close"].mean() /100
       self.weighted_std = 0
       for stock, weight in zip(self.stocks, self.weights):
            self.weighted_std += weight * stock.std_close
       self.sharpe = (self.portfolio_return - self.rf_rate) / self.weighted_std


       self.weighted_beta = 0
       for stock, weight in zip(self.stocks, self.weights):
           beta = stock.data['Close'].cov(self.sp_data['Close']) / self.sp_data['Close'].var()
           self.weighted_beta += weight * beta

    def print_portfolio(self):
        print(f"While your picks returned {self.portfolio_return:.2f}%, S&P returned {self.sp_return:.2f}%")

        if self.alpha > 0:
            print(f"Congratulations, you beat the S&P 500 by {self.alpha:.2f}%!")
        else:
            print(f"Uh oh, the S&P 500 beat you by {abs(self.alpha):.2f}%! Better luck next time!")


        if self.sharpe < 1:
            print(f"That's not great, your return came with a lot of risk, as Sharpe was calculated to be {self.sharpe:.2f}")
        elif self.sharpe < 2:  
            print(f"That's pretty good, your return came with moderate risk, as Sharpe was calculated to be {self.sharpe:.2f}")
        else:
            print(f"Great job! Your return came with minimal risk, as Sharpe was calculated to be {self.sharpe:.2f}!")

        if self.weighted_beta <1:
            print("Overall, pretty good! Your picks were less risky than the market!")
        else:
            print("Overall, could be better, your picks were more risy than the market.")
    def print_all_stocks(self):
        for stock in self.stocks:
            stock.print_important_info()
            print("---")


# In[4]:


import sys
print(sys.executable)


# In[6]:


import yfinance as yf
print("yfinance works!")


# In[25]:


msft = StockAnalyzer("MSFT", "2023-01-01", "2023-12-31")
googl = StockAnalyzer("GOOGL", "2023-01-01", "2023-12-31")
meta = StockAnalyzer("META", "2023-01-01", "2023-12-31")

msft.average_price()
googl.average_price()
meta.average_price()

portfolio = Portfolio([msft, googl, meta], [0.5, 0.3, 0.2])
portfolio.calculations()
portfolio.print_all_stocks()
portfolio.print_portfolio()





