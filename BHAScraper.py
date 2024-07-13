import requests
import json
from bhacourses import bha_courses 

import pandas as pd
import headerProxy
from raceday import *
from abandonedcatcher import AbandonedRaceCatcher
from bs4 import BeautifulSoup as BS
from bs4 import Comment
import pprint
import datetime

AUTH_TOKEN_URI = "https://www.britishhorseracing.com/feeds/v1/token/request"
BHA_RACEDAY_API_BASE = "https://www.britishhorseracing.com/feeds/v3/fixtures/"

class BhaScraper:
    def __init__(self, course, rday=None):
        self._raceday = rday

        if course != 'Towcester' and rday._date != datetime.date(2020, 6, 4):
            try:
                with requests.Session() as s:
                    #Get authentication token
                    auth_res = s.get(AUTH_TOKEN_URI, 
                                     headers = headerProxy.getRandomHeader())
                    
                    if auth_res.status_code != 200:
                        raise ValueError("Request error")
                
                    auth_res_as_json = json.loads(auth_res.content)
                    self._token = auth_res_as_json['token']
                
                    self._year = rday._year 
                    self._month = rday._month
                    self._courseName = bha_courses[course.lower()]['courseName']
                    self._courseID = bha_courses[course.lower()]['courseID']
                    
                    built_uri = self._build_uri()
                    token_header = self._get_header_dict()
                    self._data = json.loads(s.get(built_uri, headers=token_header).content)['data']
                    
                    self._bha_raceday_id = self._find_date_in_data(rday)
                    
                    raceday_data_uri = self._build_raceday_data_uri()
                    
                    data_from_races = s.get(raceday_data_uri, headers=token_header).json()['data']
                    # print(data_from_races)
                    for race_data in data_from_races:
                        print(race_data['distanceChangeText'],
                              #(race_data['distanceValue'] + race_data['distanceChange']),
                              race_data['raceTime'])
                    meeting_id = (self._raceday.get_bha_date() +"_"+ course).replace("-","_")
                    rday.di = {}
                    for race_data in data_from_races:
                        if race_data['distanceChange'] == None:
                            race_data['distanceChange'] = 0
                        
                        race_id = meeting_id + "_" + race_data['raceTime'][:-3].replace(":","")
                        dist = race_data['distanceValue'] + race_data['distanceChange'] ##isuue when no distnace change default to 0 at later time
                        rday.di[race_data['raceTime'][:-3]]= {                            
                             'dist_delta_f': round(race_data['distanceChange']/220,2),
                             'Act_dist_f': dist/220,
                             'meeting_id': meeting_id,
                             'race_id': race_id
                             }
    
                    df = pd.DataFrame()
                    for i in rday.di:
                        df = df.append(rday.di[i], ignore_index=True)   
                    
                    self.df = df
                    #df.to_csv(f"C:/racing-web-scraper/Data/scraped_data/BHA/{meeting_id}_BHA.csv", index = False)
                    #self.data()
                    
            except Exception as e:
                print(e)
        else:
            self.df =  pd.DataFrame()


    def data(self):
        return self.df
            
    def _build_uri(self):
        uri_base = "https://www.britishhorseracing.com/feeds/v3/fixtures?"
        uri_part_a = f"courseId={self._courseID}&courseName={self._courseName}&"
        uri_fields = f"fields=courseId,courseName,fixtureDate,fixtureType,fixtureSession,abandonedReasonCode,highlightTitle&"
        uri_determined = f"month={self._month}&order=desc&page=1&per_page=10&resultsAvailable=true&year={self._year}"    
        
        full_uri = uri_base + uri_part_a + uri_fields + uri_determined
        return full_uri
    
    def _build_raceday_data_uri(self):
        return BHA_RACEDAY_API_BASE + str(self._year) + "/" + str(self._bha_raceday_id) + "/races"
        
    def _get_header_dict(self):
        return {'authorization': self._token}
    
    def _find_date_in_data(self, rday):
        for rd in self._data:
            # print(self._raceday.get_bha_date() + " => " + rd['fixtureDate'])
            if rd['fixtureDate'] == rday._date.strftime("%Y-%m-%d"):
                return rd['fixtureId']
        
        return -1
                        
# BhaScraper('Newcastle', rday = RaceDay(9,3,2021))    
# if __name__ == "__main__":
#     rd = RaceDay('Doncaster', 2021, 1, 30)
#     # print(rd)
#     BHAScraper(raceday=rd)
   
   
   
   
   
   
   
   
   