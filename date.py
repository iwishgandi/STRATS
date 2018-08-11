import xlrd
import pandas as pd
import time
import logging
#from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.holiday import get_calendar, HolidayCalendarFactory, GoodFriday, AbstractHolidayCalendar, Holiday, EasterMonday, Easter, nearest_workday, next_workday, after_nearest_workday, MO
from pandas.tseries.offsets import Day, CustomBusinessDay
from pandas.tseries.offsets import BDay
from datetime import datetime
from dateutil import tz
from dateutil import parser

class CanadaTradingCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('New Years Day', month=1, day=1, observance=nearest_workday),
        Holiday('Family Day', month=2, day=1, offset=pd.DateOffset(weekday=MO(3))),
		GoodFriday,
        Holiday('Victoria Day', month=5, day=25, offset=pd.DateOffset(weekday=MO(-1))),
		Holiday('Canada Day', month=7, day=1,observance=next_workday),
        Holiday('Civic Holiday', month=8, day=1, offset=pd.DateOffset(weekday=MO(1))),
        Holiday('Labour Day', month=9, day=1, offset=pd.DateOffset(weekday=MO(1))),		
		Holiday('Thanksgiving Day', month=10, day=9, observance=nearest_workday),		
        Holiday('Remembrance Day', month=11, day=11, observance=next_workday),	
        Holiday('Christmas', month=12, day=25, observance=nearest_workday),
		Holiday('Boxing Day', month=12, day=25, observance=after_nearest_workday)
    ]

try:
	init
except NameError:
	init = True
	bndcal = get_calendar('USFederalHolidayCalendar')
	bndtradingCal = HolidayCalendarFactory('TradingCalendar', bndcal, GoodFriday)

	eqcal = get_calendar('USFederalHolidayCalendar')  # Create calendar instance
	eqcal.rules.pop(7)                                # Remove Veteran's Day rule
	eqcal.rules.pop(6)                                # Remove Columbus Day rule	
	eqtradingCal = HolidayCalendarFactory('TradingCalendar', eqcal, GoodFriday)

def get_fromxldate(xldate):
	return xlrd.xldate.xldate_as_datetime(int(xldate), 0)

def get_fromxldatetime(xldatetime):
    return xlrd.xldate.xldate_as_datetime(float(xldatetime), 0)

def excel_date_local(date1):
	temp = pd.to_datetime('1/1/1900 00:00:00').tz_localize('UTC').to_datetime()
	delta = pd.to_datetime(date1).tz_convert('UTC') - temp
	return 2 + float(delta.days) + (float(delta.seconds - (datetime.utcnow() - datetime.now()).seconds) / 86400) # Excel incorrectly assumes 1900 is a leap year, so we have to add 2, not 1
	
def excel_date(date1):
	temp = datetime(1899, 12, 30)
	delta = date1 - temp
	return float(delta.days) + (float(delta.seconds) / 86400)
        
def get_today():
	today = pd.to_datetime('today').to_datetime()
	print 'Today is ' + str(today)
	return today
	
def get_local_now():
	return pd.to_datetime('now').tz_localize('UTC').tz_convert('US/Eastern').to_datetime()	

def get_now():
	return pd.to_datetime('now').to_datetime()

def get_mindatetime():
	return pd.to_datetime('1900-01-01 00:00:00').to_datetime()
	
def get_offsetequitiesbizday(refdate, offset):
	bday_bond = CustomBusinessDay(calendar=eqtradingCal())
	return refdate + offset * bday_bond
	
def get_offsetbizday(refdate, offset):
	bday_bond = CustomBusinessDay(calendar=bndtradingCal())
	return refdate + offset * bday_bond

def get_canada_offsetbizday(refdate, offset):
	bday_bond = CustomBusinessDay(calendar=CanadaTradingCalendar())
	return refdate + offset * bday_bond	
	
def get_offsetweekday(refdate, offset):
	return refdate + offset * BDay(1)
	
def get_prevbizday(refdate):
	return get_offsetbizday(refdate, -1)

def get_prevequitiesbizday(refdate):
	return get_offsetequitiesbizday(refdate, -1)

def get_nextequitiesbizday(refdate):
	return get_offsetequitiesbizday(refdate, 1)

def get_prevequitiesbizday(refdate):
	return get_offsetequitiesbizday(refdate, 1)

def get_canada_prevequitiesbizday(refdate):
	return get_canada_offsetbizday(refdate, -1)
	
def get_nextbizday(refdate):
	return get_offsetbizday(refdate, 1)

def get_canada_nextbizday(refdate):
	return get_canada_offsetbizday(refdate, 1)	
	
def is_canada_holiday(testdate):
	#logging.info(CanadaTradingCalendar.rules)
	bday_bond = CustomBusinessDay(calendar=CanadaTradingCalendar())
	prevweekday = testdate - BDay(1)
	return (prevweekday + (1 * bday_bond)) != (prevweekday + BDay(1))
	
def is_holiday(testdate):
	bday_bond = CustomBusinessDay(calendar=bndtradingCal())
	#bday_bond = CustomBusinessDay(calendar=USFederalHolidayCalendar())
	prevweekday = testdate - BDay(1)
	return (prevweekday + (1 * bday_bond)) != (prevweekday + BDay(1))
	
def is_bizdayafterholiday(testdate):
	bday_bond = CustomBusinessDay(calendar=bndtradingCal())
	#bday_bond = CustomBusinessDay(calendar=USFederalHolidayCalendar())
	return (testdate - (1 * bday_bond)) != (testdate - BDay(1))

def is_canada_bizdayafterholiday(testdate):
	bday_bond = CustomBusinessDay(calendar=CanadaTradingCalendar())
	#bday_bond = CustomBusinessDay(calendar=USFederalHolidayCalendar())
	return (testdate - (1 * bday_bond)) != (testdate - BDay(1))
	
def convertdateformat(dt, format1, format2):
	dt2 = datetime.strptime(dt, format1)
	return dt2.strftime(format2)

def parsedate(dt):
	return parser.parse(dt)
	
def utctolocal(utc):
	utc = utc.replace(tzinfo=tz.tzutc())
	et = utc.astimezone(tz.tzlocal())
	tm = time.mktime(et.timetuple())
	return datetime.fromtimestamp(tm)