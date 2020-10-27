from __future__ import (absolute_import, division, print_function, unicode_literals)

import csv
import backtrader as bt  # Import the backtrader platform
import datetime  # For datetime objects
from fade_close_long import FadeCloseStrategy
# Set variables
nestlist = []
# Set initial capital
icap = 100000

# Set position size - Percent of capital to deploy per trade
PercSize = 98

# Set percent trailing stop
PercTrail = 0

# Timeframe for the analysis
start_date = [1993,1,1]
end_date = [2020,10,1]

# define helper functions
def pretty_print(format, *args):
    print(format.format(*args))

def exists(object, *properties):
    for property in properties:
        if not property in object: return False
        object = object.get(property)
    return True

def writeTradeAnalysis(cerebro, analyzers, symbol, nestlist):
    if hasattr(analyzers, 'ta'):
        nestlist.append([symbol])
        ta = analyzers.ta.get_analysis()

        nestlist[-1].append(ta.total.open)          if exists(ta, 'total', 'open'  ) else None
        nestlist[-1].append(ta.total.closed)        if exists(ta, 'total', 'closed') else None
        nestlist[-1].append(ta.won.total)           if exists(ta, 'won',   'total' ) else None
        nestlist[-1].append(ta.lost.total)          if exists(ta, 'lost',  'total' ) else None

        nestlist[-1].append(ta.streak.won.longest)  if exists(ta, 'streak', 'won',  'longest') else None
        nestlist[-1].append(ta.streak.lost.longest) if exists(ta, 'streak', 'lost', 'longest') else None

        nestlist[-1].append(ta.pnl.net.total)       if exists(ta, 'pnl', 'net', 'total'  ) else None
        nestlist[-1].append(ta.pnl.net.average)     if exists(ta, 'pnl', 'net', 'average') else None

    if hasattr(analyzers, 'drawdown'):
        nestlist[-1].append(analyzers.drawdown.get_analysis()['drawdown'])
    if hasattr(analyzers, 'sharpe'):
        nestlist[-1].append(analyzers.sharpe.get_analysis()['sharperatio'])
    if hasattr(analyzers, 'vwr'):
        nestlist[-1].append(analyzers.vwr.get_analysis()['vwr'])
    if hasattr(analyzers, 'sqn'):
        nestlist[-1].append(analyzers.sqn.get_analysis()['sqn'])

def printTradeAnalysis(cerebro, analyzers):
    format = "  {:<24} : {:<24}"
    NA     = '-'

    print('Backtesting Results')
    if hasattr(analyzers, 'ta'):
        ta = analyzers.ta.get_analysis()

        openTotal         = ta.total.open          if exists(ta, 'total', 'open'  ) else None
        closedTotal       = ta.total.closed        if exists(ta, 'total', 'closed') else None
        wonTotal          = ta.won.total           if exists(ta, 'won',   'total' ) else None
        lostTotal         = ta.lost.total          if exists(ta, 'lost',  'total' ) else None

        streakWonLongest  = ta.streak.won.longest  if exists(ta, 'streak', 'won',  'longest') else None
        streakLostLongest = ta.streak.lost.longest if exists(ta, 'streak', 'lost', 'longest') else None

        pnlNetTotal       = ta.pnl.net.total       if exists(ta, 'pnl', 'net', 'total'  ) else None
        pnlNetAverage     = ta.pnl.net.average     if exists(ta, 'pnl', 'net', 'average') else None

        pretty_print(format, 'Open Positions', openTotal   or NA)
        pretty_print(format, 'Closed Trades',  closedTotal or NA)
        pretty_print(format, 'Winning Trades', wonTotal    or NA)
        pretty_print(format, 'Loosing Trades', lostTotal   or NA)
        print('\n')

        pretty_print(format, 'Longest Winning Streak',   streakWonLongest  or NA)
        pretty_print(format, 'Longest Loosing Streak',   streakLostLongest or NA)
        pretty_print(format, 'Strike Rate (Win/closed)', (wonTotal / closedTotal) * 100 if wonTotal and closedTotal else NA)
        print('\n')

        pretty_print(format, 'Inital Portfolio Value', '${}'.format(icap))
        pretty_print(format, 'Final Portfolio Value',  '${}'.format(cerebro.broker.getvalue()))
        pretty_print(format, 'Net P/L',                '${}'.format(round(pnlNetTotal,   2)) if pnlNetTotal   else NA)
        pretty_print(format, 'P/L Average per trade',  '${}'.format(round(pnlNetAverage, 2)) if pnlNetAverage else NA)
        print('\n')

    if hasattr(analyzers, 'drawdown'):
        pretty_print(format, 'Drawdown', '${}'.format(analyzers.drawdown.get_analysis()['drawdown']))
    if hasattr(analyzers, 'sharpe'):
        pretty_print(format, 'Sharpe Ratio:', analyzers.sharpe.get_analysis()['sharperatio'])
    if hasattr(analyzers, 'vwr'):
        pretty_print(format, 'VRW', analyzers.vwr.get_analysis()['vwr'])
    if hasattr(analyzers, 'sqn'):
        pretty_print(format, 'SQN', analyzers.sqn.get_analysis()['sqn'])
    print('\n')

    """print('Transactions')
    format = "  {:<24} {:<24} {:<16} {:<8} {:<8} {:<16}"
    pretty_print(format, 'Date', 'Amount', 'Price', 'SID', 'Symbol', 'Value')
    for key, value in analyzers.txn.get_analysis().items():
        pretty_print(format, key.strftime("%Y/%m/%d %H:%M:%S"), value[0][0], value[0][1], value[0][2], value[0][3], value[0][4])
"""

# Run Main Program
# loop through a column of a csv file to create list of tickers
symbols = []

with open('stock_tickers.csv', 'r') as rf:
    reader = csv.reader(rf, delimiter=',')
    for row in reader:
      symbols.append(row[0])
symbols = symbols[1:]

for symbol in symbols:
    # Create an instance of cerebro
    cerebro = bt.Cerebro(stdstats=False)

    # Be selective about what we chart
    cerebro.addobserver(bt.observers.Broker)
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Value)
    cerebro.addobserver(bt.observers.DrawDown)
    cerebro.addobserver(bt.observers.Trades)

    # Set the investment capital
    cerebro.broker.setcash(icap)

    # Set position size
    cerebro.addsizer(bt.sizers.PercentSizer, percents=PercSize)

    # Add our strategy
    cerebro.addstrategy(FadeCloseStrategy)

    # Create a Data Feed
    datapath = 'stock_data/{}.csv'.format(symbol) # change backslash for mac / vs pc \

    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # ensure the from and to are in range of the data
        fromdate=datetime.datetime(start_date[0], start_date[1], start_date[2]),
        todate=datetime.datetime(end_date[0], end_date[1], end_date[2]),
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Add analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='ta')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0145, annualize=True, timeframe=bt.TimeFrame.Days)
    cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.Transactions, _name='txn')

    # Run our Backtest
    backtest = cerebro.run()
    backtest_results = backtest[0]
    # check data
    if symbol == 'SHY':
        # Print some analytics
        printTradeAnalysis(cerebro, backtest_results.analyzers)
    writeTradeAnalysis(cerebro, backtest_results.analyzers, symbol, nestlist)

# opening the csv file in 'a+' mode 
file = open('asset_performance.csv', 'a+', newline ='') 
  
# writing the data into the file 
with file:     
    write = csv.writer(file) 
    write.writerows(nestlist)
# Finally plot the end results
# cerebro.plot(style='candlestick', volume=False)