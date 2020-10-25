import csv
import pandas
from pandas_datareader import data
from datetime import datetime

# create a string variable of today's date
current_date = datetime.now()
end_date = current_date.strftime("%Y-%m-%d")
# old date hopefully long enough ago that it will incorporate all the data any particular ticker requires
start_date = '1980-01-01'
# data source currently yahoo finance
web_data = 'yahoo'

# loop through a column of a csv file to create list of tickers
symbols = []

with open('stock_tickers.csv', 'r') as rf:
    reader = csv.reader(rf, delimiter=',')
    for row in reader:
      symbols.append(row[0])
symbols = symbols[1:]


# loop through list of tickers pull historical value for each ticker 
# and write to a separate csv file for each ticker
for symbol in symbols:
    price_history = data.DataReader(symbol,web_data,start_date,end_date)
    df = pandas.DataFrame(price_history)
    columnsTitles=["Open","High","Low","Close","Adj Close","Volume"]
    df=df.reindex(columns=columnsTitles)
    df.to_csv('stock_data\{}.csv'.format(symbol))
    print(symbol)
