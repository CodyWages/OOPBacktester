import yfinance as yf
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt

class Backtest:

    def __init__(self, symbol):
        self.symbol = symbol
        self.df = yf.download(self.symbol,start='ENTER START DATE')
        if self.df.empty:
            print('NO DATA')
        else:
            self.calc_indicators()
            self.generate_signals()
            self.buy_sell_loop()
            self.profit = self.calc_profit()
            self.biggestW = self.profit.max()
            self.biggestL = self.profit.min()
            self.cumulProfit = (self.profit + 1).prod() - 1
            self.tradeCount = self.trade_count()

    def calc_indicators(self):
        # ENTER THE INDICATORS NEEDED FOR generate_signals() FUNCTION
        self.df['ma_20'] = self.df.Close.rolling(20).mean()
        self.df['vol'] = self.df.Close.rolling(20).std()
        self.df['upper_bb'] = self.df.ma_20 + (2 * self.df.vol)
        self.df['lower_bb'] = self.df.ma_20 - (2 * self.df.vol)
        self.df['rsi'] = ta.momentum.rsi(self.df.Close,window=6)
        self.df.dropna(inplace=True)

    def generate_signals(self):
        conditions = ['ENTER BUY SIGNAL CONDITIONS','ENTER SELL SIGNAL CONDITIONS']
        choices = ['Buy','Sell']
        self.df['signal'] = np.select(conditions,choices)
        self.df.signal = self.df.signal.shift()
        self.df.dropna(inplace=True)

    def buy_sell_loop(self):
        position = False
        buyDates,sellDates = [],[]

        for index, row in self.df.iterrows():
            if not position and row['signal'] == 'Buy':
                position = True
                buyDates.append(index)

            if position and row['signal'] == 'Sell':
                position = False
                sellDates.append(index)

        self.buyArray = self.df.loc[buyDates].Open
        self.sellArray = self.df.loc[sellDates].Open

    def calc_profit(self):
        if self.buyArray.index[-1] > self.sellArray.index[-1]:
            self.buyArray = self.buyArray[:-1]
        return (self.sellArray.values - self.buyArray.values) / self.buyArray.values

    def plot_chart(self):
        plt.figure(figsize=(10,5))
        plt.plot(self.df.Close)
        plt.scatter(self.buyArray.index, self.buyArray.values, marker='^', c='g')
        plt.scatter(self.sellArray.index, self.sellArray.values, marker='v', c='r')
        plt.show()

    def trade_count(self):
        buys = self.buyArray
        sells = self.sellArray
        return len(buys) + len(sells)

instance = Backtest('ENTER ASSET SYMBOL')

print(f'\nCumulative Profit: {instance.cumulProfit * 100} %\nBiggest Win: {instance.biggestW * 100} %\nBiggest Loss: {instance.biggestL * 100} %\nNumber of Trades: {instance.tradeCount}')
instance.plot_chart()
