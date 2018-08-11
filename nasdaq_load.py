import datetime
import json
import ast
import time
import pandas as pd
import traceback
import logging
import select
import imp
import numpy as np
from datetime import timedelta
from collections import defaultdict
import sys
import inspect
import os
import zlib
import base64
import urllib2
import logging
import earnings as earningutil
import date as dateutil
import fix_yahoo_finance as yf

from pandas_datareader import data as pdata
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(message)s')

data_source = "google"
yf.pdr_override()

def close_oneday(ticker, day):
	#return pdata.DataReader(ticker, "yahoo", day, day).ix[day.strftime("%Y-%m-%d")]["Close"]
	day_str = day.strftime("%Y-%m-%d")
	print day_str
	return pdata.get_data_yahoo(ticker, start=day_str, end=day_str).ix[day_str]["Close"]

def price_days(ticker, start_date, end_date):
	df = data.DataReader([ticker], data_source, start_date, end_date).minor_xs(ticker)
	df.index.name = "asofts"
	df.columns = ["openpx", "highpx","lowpx","closepx","volume"]
	return df

def high_low_analyze(ticker,start_date,end_date):
	try:
		end_date = datetime.datetime.today().strftime("%Y-%m-%d")
		prev_high = prev_low = -1
		df = price_days(ticker,start_date,end_date)
		high_low_list = list(zip(df.highpx, df.lowpx))
		logging.info("IN PAST {0} DAYS:".format(len(high_low_list)))
		day = day_low = day_high = 0
		for (high,low) in high_low_list:
			if high > prev_high:
				if day > day_high + 1:	
					logging.info("LOW: PX {0:.2f}, DAY {1}, DOWN {2:.2f}\nHIGH: PX {3:.2f}, DAY {4}, UP {5:.2f}, ".format(prev_low, day_low, (prev_high-prev_low)*100/prev_high, high, day, (high-prev_low)*100/prev_low))
				prev_high = high
				day_high = day	
				prev_low = low
			if low <= prev_low:
				prev_low = low
				day_low = day
			day += 1	
		last_px = df["closepx"].tolist()[-1]
		logging.info("LAST PX {0:.2f}, DOWN_FROM_ALL_HIGH {1:.2f}".format(last_px,(prev_high-last_px)*100/prev_high))	
	except:
		logging.error(traceback.format_exc())	

tickers = ["AAPL","FB","DBX","NVDA","BABA","TSLA","AMZN","PSTG","AMD","NFLX","GOOG","PYPL","SQ","SNAP"]
for ticker in tickers:
	print ticker
	df = pdata.get_data_yahoo(ticker, start="2009-1-1", end="2018-6-1")
	dict1 = df["Close"].to_dict()
	close_dict = {k.date():v for k,v in dict1.items()}
	dict2 = df["Open"].to_dict()
	open_dict = {k.date():v for k,v in dict2.items()}	
	earnings = earningutil.read_earnings(ticker)
	prev = -1.0
	print ("\nDATE		PX		PCT		OPEN	   PCT		2DAY	   PCT		HIGH	   PCT		LOW	   PCT")
	earnings.reverse()
	#p1:close px of earning day, #p2:px of two days after earnings day, #p3:high between earnings, #p4:low between earnings, #p5:open px of next day after earnings
	for idx, e_date in enumerate(earnings):
		if dateutil.get_offsetequitiesbizday(e_date,2).date() < datetime.datetime.now().date():
			p1 = close_dict[e_date]				
			count = 0
			i = 1
			while(count!=2):
				offset_date = dateutil.get_offsetequitiesbizday(e_date,i).date()
				if offset_date in close_dict:
					count += 1		
					if count == 2:
						p2 = close_dict[offset_date]	
					elif count == 1:
						p5 = open_dict[offset_date]					
				i += 1	
			p3 = p4 = p1
			if idx<len(earnings)-1:
				d = e_date
				while d <= earnings[idx+1]:
					if d in close_dict:
						p3,p4 = max(p3,close_dict[d]),min(p4,close_dict[d])
					d += datetime.timedelta(days=1)		
			print ("%s-%02s-%02s	%5.2f	%11.2f	%12.2f	%6.2f	%12.2f	%6.2f	%12.2f	%6.2f	%12.2f	%6.2f" % (e_date.year, e_date.month, e_date.day, p1,0 if prev==-1.0 else (p1-prev)*100/prev,p5,(p5-p1)*100/p1,p2,(p2-p1)*100/p1,p3,(p3-p1)*100/p1,p4,(p4-p1)*100/p1))
			prev = p1	
