import csv
import yfinance as yf
urls = []
with open('stock_tickers.csv', 'r') as rf:
    reader = csv.reader(rf, delimiter=',')
    for row in reader:
      urls.append(row[0])
urls = urls[1:]

for url in urls:
    tickerTag = yf.Ticker(url)
    tickerTag.history(period="max",actions=False).to_csv("stock_data\{}.csv".format(url))
