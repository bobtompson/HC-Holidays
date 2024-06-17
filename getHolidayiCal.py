#!/usr/bin/env python
""" getHolidayiCal.py
    Parses Highline College's HR website for holidays posted and
    makes an ical files to import to a standard calendar
    Made with python 3.11 should run in any 3.x
    
    To install required libraries:
        "pip install pandas requests ics bs4 lxml"
     OR: "pip install -r requirements.txt"
    
    To run: python getHolidayiCal.py
"""

__author__ = "Kyle Evans <kevans@highline.edu"
__copyright__ = "Copyright 2023, Highline College"
__version__ = "0.3"

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import pandas as pd
from ics import Calendar, Event
from io import StringIO

pd.set_option('display.max_columns', None)
pd.set_option('max_colwidth', None)

""" Takes a string and try to make a valid datetime obj
    Returns a datetime obj or False value for invalid string format
"""


def validate_date(date_text):
    try:
        return datetime.strptime(date_text, '%A, %B %d %Y')
    except ValueError:
        return False


""" Takes a string and try to make a valid datetime obj
    Returns a datetime obj or False value for no date found
"""


def validate_year(date_text):
    try:
        return parser.parse(date_text, fuzzy=True)
    except parser._parser.ParserError:
        return False


""" Takes a year string from the years array, and grabs the corresponding
    table and then converts all the dates strings and makes a calendar file 
"""


def processYear(year, count, df_list):
    my_holidays = df_list[count]
    # normalize column names to upper
    my_holidays.columns = my_holidays.columns.str.upper()

    cal = Calendar()

    # Iterate over dataframe object
    for index, event in my_holidays.iterrows():
        event_year = year
        event_date_string = event['DATE'] + " " + event_year
        event_holiday_name = f"Highline Holiday: {event['HOLIDAY']}";

        dte = validate_date(event_date_string)
        if (dte != False):
            ev = Event()
            print(f"Event {index}:")
            print(f"{event_holiday_name} - {dte}")
            ev.name = event_holiday_name
            ev.begin = f"{dte}"
            cal.events.add(ev)

    # Create ical file
    with open(f"highline_holidays_{event_year}.ics", 'w') as f:
        f.writelines(cal.serialize_iter())


URL = 'http://humanresources.highline.edu/benefits/holiday-schedule/'
res = requests.get(URL)
# Read Tables
# df_list = pd.read_html(res.text)
df_list = pd.read_html(StringIO(str(res.text)))
soup = BeautifulSoup(res.content, "html.parser")

# Grab Years
# Make a list of all H1 tags with a valid year
years = []
for year in soup.find_all('h1'):
    thisyear = validate_year(year.text)
    if (thisyear != False):
        years.append(str(thisyear.strftime('%Y')))

count = 0
for year in years:
    print(f"-----[Events for {year}]------")
    processYear(year, count, df_list)
    count += 1
