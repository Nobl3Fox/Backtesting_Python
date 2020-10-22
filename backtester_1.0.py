from __future__ import (absolute_import, division, print_function, unicode_literals)


import backtrader as bt  # Import the backtrader platform
import datetime  # For datetime objects
from strategy import TestStrategy

# Ideas
# https://github.com/amberdata/jupyter-notebook/blob/master/market/Backtest%20BTC_LO_MCD_SMA_STF_Perct_TS.py
# Create a cerebro entity
cerebro = bt.Cerebro()

# Set our desired cash start
cerebro.broker.setcash(100000.0)

# Add a Percentage sizer according to the stake
cerebro.addsizer(bt.sizers.PercentSizer, percents=98)
#cerebro.addsizer(bt.sizers.FixedSize, stake=1000)

# Set broker commission
cerebro.broker.setcommission(commission=0)

# Set tax rate (Work in Progress...) 

# Create a Data Feed
datapath = 'stock_data\SPY.csv'

data = bt.feeds.YahooFinanceCSVData(
    dataname=datapath,
    # ensure the from and to are in range of the data
    fromdate=datetime.datetime(2008, 1, 1),
    todate=datetime.datetime(2020, 9, 30),
    reverse=False)

# Add the Data Feed to Cerebro
cerebro.adddata(data)

# Add strategy to Cerebro
cerebro.addstrategy(TestStrategy)

# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Run over everything
cerebro.run()

# Plot 
cerebro.plot()
# cerebro.plot(style='candlestick', volume=False)
# cerebro.addanalyzer(bt.analyzers.AnnualReturn.print, _name='myanreturns')
# print(bt.analyzers.SharpeRatio())
# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
