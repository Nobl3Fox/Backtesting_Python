import csv
# import yfinance as yf
from datetime import datetime, timedelta
import time
import requests, pandas, lxml
from lxml import html

# THIS WAS A LOT OF WORK AND THINK AND I DIDN'T END UP 

# reference
# https://medium.com/c%C3%B3digo-ecuador/how-to-scrape-yahoo-price-history-data-with-python-52751eee9b
# https://medium.com/c%C3%B3digo-ecuador/how-to-scrape-yahoo-stock-price-history-with-python-b3612a64bdc6

# A normal datetime object creates an invalid URL, thus a date in epoch time format must be passed 
# returns a string 
def format_date(date_datetime):
  date_timetuple = date_datetime.timetuple()
  date_mktime = time.mktime(date_timetuple)
  date_int = int(date_mktime)
  date_str = str(date_int)
  return date_str

# Request headers contain information your browser sends to the target web server when it requests data. 
# It identifies who you are and what tools you are using to the website you are browsing.
# returns a dictionary object 
def subdomain(symbol, start, end, filter='history'):
  subdoma="/quote/{0}/history?period1={1}&period2={2}&interval=1d&filter={3}&frequency=1d"
  subdomain = subdoma.format(symbol, start, end, filter)
  return subdomain
 
def header_function(subdomain):
  hdrs =  {"authority": "finance.yahoo.com",
           "method": "GET",
           "path": subdomain,
           "scheme": "https",
           "accept": "text/html",
           "accept-encoding": "gzip, deflate, br",
           "accept-language": "en-US,en;q=0.9",
           "cache-control": "no-cache",
           "dnt": "1",
           "pragma": "no-cache",
           "sec-fetch-mode": "navigate",
           "sec-fetch-site": "same-origin",
           "sec-fetch-user": "?1",
           "upgrade-insecure-requests": "1",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64)"}   
  return hdrs

def scrape_page(url, header):
  page = requests.get(url, headers=header)
  element_html = html.fromstring(page.content)
  # the XPath method on the HTML element will return a list of tables
  table = element_html.xpath('//table')
  # use the tostring function of the etree module to turn the table element into a byte string
  table_tree = lxml.etree.tostring(table[0], method='xml')
  panda = pandas.read_html(table_tree)
  return panda

if __name__ == '__main__':
  # creates an empty list that is populated when a column of ticker symbols are read in from a csv file
  symbols = ['VEA']
  """
  with open('stock_tickers.csv', 'r') as rf:
    reader = csv.reader(rf, delimiter=',')
    for row in reader:
      symbols.append(row[0])
  symbols = symbols[1:]
  """
    
  # loops through symbols list to pull yahoo finance data and create a csv for each ticker
  for symbol in symbols:
    # creates two datetime objects, one for the start date and another for the end date. 
    # Then, the code passes those datetime objects into the format_date function 
    # to create the epoch time strings that we will use to format the URL in our Yahoo Finance header.
    dt_start = datetime.today() - timedelta(days=365) # timedelta command in the dt_start variable sets a date in the past which is 365 days before today’s date.
    # If you want to set the start date in the future change the minus sign to a plus symbol 
    dt_end = datetime.today()
    # start and end of time window for ticker data being scraped
    start = format_date(dt_start)
    end = format_date(dt_end)
    
    sub = subdomain(symbol, start, end)
    header = header_function(sub)
      
    base_url = 'https://finance.yahoo.com'
    url = base_url + sub
    price_history = scrape_page(url, header)
    df = pandas.DataFrame(price_history)
    df.to_csv('{}.csv'.format(symbol))

"""
with open('stock_tickers.csv', 'r') as rf:
  reader = csv.reader(rf, delimiter=',')
  for row in reader:
    symbols.append(row[0])
symbols = symbols[1:]

for symbol in symbols:
  tickerTag = yf.Ticker(symbol)
  print(tickerTag.history(period="max")) #.to_csv("stock_data\{}.csv".format(url))
    
"""