import backtrader as bt
import datetime

# Strategy Reference 
# Use a mean reversion play: Fade Close Outside Previous Day's Range
# https://adamhgrimes.com/moving-averages-digging-deeper/
class FadeCloseStrategy(bt.Strategy):
    params = dict(
        stop_loss=0.08,
        trail=False,
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" and "low" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.datalow = self.datas[0].low
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.stop_price = 0
        self.tax_rate = 0.45
        self.principle = self.broker.getvalue()
        self.nyear = None
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.stop_price = self.order.executed.price * (1.0 - self.p.stop_loss)
                self.bar_executed = len(self)
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f, Stop %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     self.stop_price
                     ))

                
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
                self.bar_executed = None
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def taxes(self):
        # check if you have profit
        # if do not exit taxes
        if self.principle >= self.broker.getvalue():
            return
        else: # update principle by adding net profits
            profit = self.broker.getvalue() - self.principle
            tx = profit*self.tax_rate
            nprofit = profit - tx
            self.principle += nprofit
            # deduct tax from broker
            self.log('Taxes Payed, gross %.2f, taxes %.2f, net %.2f' % (
                self.principle + tx,
                tx,
                self.principle
            ))
            self.broker.add_cash(-tx)

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        #self.order_target_percent(target=1.0)
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            if self.nyear == None:
                self.nyear =  int(str(self.datas[0].datetime.date(0))[0:4])
            if int(str(self.datas[0].datetime.date(0))[0:4]) > self.nyear:
                print("FIX ME")
                self.taxes()
                self.nyear = int(str(self.datas[0].datetime.date(0))[0:4])
            # Not yet ... we MIGHT BUY if ...
            if self.dataclose[0] < self.datalow[-1]:

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5): 
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.stop_price = 0
                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()
            elif self.stop_price >= self.dataclose:
                self.log('STOP SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()
                
        
 
    

    

