from __future__ import (absolute_import, division, print_function, unicode_literals)


import backtrader as bt  # Import the backtrader platform
import datetime  # For datetime objects
from strategy import TestStrategy


# Create a cerebro entity
cerebro = bt.Cerebro()

datapath = 'oracle.csv'

# Create a Data Feed
data = bt.feeds.YahooFinanceCSVData(
    dataname=datapath,
    # Do not pass values before this date
    fromdate=datetime.datetime(2000, 1, 1),
    # Do not pass values after this date
    todate=datetime.datetime(2000, 12, 31),
    reverse=False)

# Add the Data Feed to Cerebro
cerebro.adddata(data)

# Add strategy to Cerebro
cerebro.addstrategy(TestStrategy)

# Set our desired cash start
cerebro.broker.setcash(100000.0)

# Print out the starting conditions
print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

# Run over everything
cerebro.run()

# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
