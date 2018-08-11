import requests
import logging
import traceback
import datetime
import BeautifulSoup
import bs4
import re
import time
from bs4 import BeautifulSoup
from yahoo_earnings_calendar import YahooEarningsCalendar
from lxml import html
from datetime import timedelta

try:
	base_url = "https://seekingalpha.com/symbol/"
	tickers = ["AAPL","GOOG","AMZN","TSLA","PSTG","FB","NFLX","NVDA","BABA","MSFT","BIDU","PYPL","AMD"]
	header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36"}
	for t in tickers:
		print t
		r = requests.get(base_url+t+"/earnings",headers=header)
		soup = BeautifulSoup(r.content, "html.parser")
		print r.content
		spans = soup.find_all("span", attrs={"class":"title-period"})
		for span in spans:
		    if span.string.startswith("Q"):
		    	print span.string
except:
	logging.error(traceback.format_exc())					