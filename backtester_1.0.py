from __future__ import (absolute_import, division, print_function, unicode_literals)


import backtrader as bt  # Import the backtrader platform
import datetime  # For datetime objects
from fade_close_long import FadeCloseStrategy

# https://www.backtrader.com/docu/quickstart/quickstart/
# Ideas
# https://github.com/amberdata/jupyter-notebook/blob/master/market/Backtest%20BTC_LO_MCD_SMA_STF_Perct_TS.py

# Set Variables
# Create a Data Feed
datapath = 'stock_data/UPRO.csv' # change backslash for mac / vs pc \
# Set initial capital
icap = 100000
# Set position size - Percent of capital to deploy per trade
PercSize = 99

# Timeframe for the analysis
start_date = [2010,1,1]
end_date = [2015,2,1]

# define helper functions
def pretty_print(format, *args):
    print(format.format(*args))

def exists(object, *properties):
    for property in properties:
        if not property in object: return False
        object = object.get(property)
    return True

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

    print('Transactions')
    format = "  {:<24} {:<24} {:<16} {:<8} {:<8} {:<16}"
    pretty_print(format, 'Date', 'Amount', 'Price', 'SID', 'Symbol', 'Value')
    for key, value in analyzers.txn.get_analysis().items():
        pretty_print(format, key.strftime("%Y/%m/%d %H:%M:%S"), value[0][0], value[0][1], value[0][2], value[0][3], value[0][4])

# main code
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

# Set leverage/commission annual commission for leverage is 1.5% average holding period is 5 days adjusted for 1 year
cerebro.broker.setcommission(commission=(0.015/(365/5)), leverage=200)

# Set position size
cerebro.addsizer(bt.sizers.PercentSizer, percents=PercSize)

# Add our strategy
cerebro.addstrategy(FadeCloseStrategy)

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
printTradeAnalysis(cerebro, backtest_results.analyzers)

# Plot 
# Finally plot the end results
cerebro.plot(style='candlestick', volume=False)
# Print out the final result
print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
