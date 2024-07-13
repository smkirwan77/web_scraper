##this file will be used to auto run the basic scraper which will then return data reequired to autorun the TPD scraper

from raceday import *
import datetime


#bit too long and conveluted BufferErrorit gives me the scope to change the deltas if for some reason I want to do more then one day.
today = datetime.date.today()
yesterday = today - datetime.timedelta(days = 4)

start_date = yesterday
end_date = today 

delta = timedelta(days=1)
while start_date <= end_date:

    r = RaceDay(start_date.day,start_date.month,start_date.year)
    #r.scrapeCourses()
    r.scrapeResults()
    r.splitData()
    start_date += delta

print('hello')
x = input()