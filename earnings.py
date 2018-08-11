import requests
import logging
import traceback
import datetime
import BeautifulSoup
import bs4
import re
import time
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from yahoo_earnings_calendar import YahooEarningsCalendar
from lxml import html
from datetime import timedelta
from datetime import datetime
from selenium.webdriver.common.by import By
from yahoo_earnings_calendar import YahooEarningsCalendar
from yahoo_finance import Share


logging.basicConfig(level=logging.INFO, format='%(message)s')


def read_news():
	try:
		browser = webdriver.Chrome()
		browser.get("https://seekingalpha.com/symbol/GOOG/news")
		time.sleep(3)
		elem = browser.find_element_by_tag_name("body")
		no_of_pagedowns = 5
		while no_of_pagedowns:
		    elem.send_keys(Keys.PAGE_DOWN)
		    time.sleep(1)
		    no_of_pagedowns-=1
		html = browser.page_source    
		header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36"}
		soup = BeautifulSoup(html, "html.parser")
		titles = soup.find_all("a", attrs={"class":"market_current_title"})
		for title in titles:
		    print title
		spans = soup.find_all("span", attrs={"class":"date pad_on_summaries"})
		for span in spans:
			print span
		browser.dispose()
	except:
		logging.error(traceback.format_exc())

'''
def read_earnings(ticker):
	base_url = "https://seekingalpha.com/symbol/"
	header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36"}
	r = requests.get(base_url+ticker+"/earnings",headers=header)
	soup = BeautifulSoup(r.content, "html.parser")
	titles = soup.find_all("h4", {"class":["panel-title earning-title"]})
	raw_earnings = []
	earning_list = []
	return_list = []
	for title in titles:
		soup = BeautifulSoup(str(title),"html.parser")
		spans = soup.findAll(["span","em"])	
		for span in spans:
			if span.text and not span.text.startswith("EPS"):
				raw_earnings.append(span.text)
	for e in raw_earnings:
		earning_list.append(datetime.strptime(e[-8:],"%m-%d-%y").date() if e.startswith("Q") else ("beat" if e.startswith("beat") else ("miss" if e.startswith("missed") else "inline")))			
	for v1,v2,v3 in zip(*[iter(earning_list)]*3):
		return_list.append([v1,v2,v3])
	return return_list[::-1][4:]
'''	

def read_earnings(ticker):
	base_url = "https://www.zacks.com/stock/research/"+ticker+"/earnings-announcements"
	header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36"}
	r = requests.get(base_url,headers=header)
	JSON = re.compile('document.obj_data = ({.*?});', re.DOTALL)
	matches = JSON.search(r.content)
	json_str = matches.group(1)
	data = json.loads(json_str)
	earnings = data["earnings_announcements_earnings_table"]
	chinese_companies = ["BABA"] 
	return [datetime.strptime(e[0],"%m/%d/%Y").date() if ticker not in chinese_companies else (datetime.strptime(e[0],"%m/%d/%Y").date()-timedelta(days=1)) for e in earnings]
