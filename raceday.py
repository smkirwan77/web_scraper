#results scaper of a day user inputs a date in int format
from datetime import date, timedelta
from bs4 import BeautifulSoup as BS
import requests
from intDistb import *
#from intDist import *
import numpy as np
import conversions
#from BHAScraper import * 
import pandas as pd
from lenghtpersecond import lps
from ATRcourses import courses
import datetime
import time
import seaborn as sns
sns.set_theme(style="whitegrid") ### might have to put this into the function below. we will see in time. 
sns.color_palette("Spectral", as_cmap=True) #this changes the relplot, hue is different in the lm plot


# start_date = date(2021, 9, 5)
# end_date = date(2021, , )
# delta = timedelta(days=1)
# while start_date <= end_date:

#     r = RaceDay(start_date.day,start_date.month,start_date.year)
#     #r.scrapeCourses()
#     r.scrapeResults()
#     r.splitData()
#     start_date += delta


class RaceDay():
    def __init__(self, d , m, y):
        self._year, self._month, self._day = y , m,  d
        self._date = datetime.date(y, m, d)
        self.raceday_url = f"https://www.racingpost.com/results/{self._date}"
        self.meetings = []
        
        #self.scrapeResults() #this will automatically scrape otherwise you could manually do rday.scrapeResults()
        
    #scrape courses can be used to create a fixture list. if data is fully scraped for a period of time in the past this is not much use
    def scrapeCourses(self):
        raceday_resp = requests.get(self.raceday_url)
        raceday_content = raceday_resp.content
        soup = BS(raceday_resp.content, "html.parser")

        List = ['(ARG)', '(AUS)', '(BHR)', '(BRZ)', '(CAN)', '(CHI)', '(CZE)' , '(DEN)', '(FR)', '(GER)', '(HK)', 
                '(IND)', '(ITY)', '(JER)', '(JPN)', '(KOR)', '(KSA)', '(NOR)', '(NZ)', '(PER)', '(QA)', '(SAF)', '(SIN)',
                '(SPA)', '(SWE)', '(SWI)', '(TUR)','(UAE)', '(URU)', '(USA)', 'SCOOP', 
                'ABANDONED', '(ARAB)','Free', 'WORLDWIDE']
        courses = []
        self.meetings = []

        for i in soup.find_all('h2', class_= 'rp-raceCourse__row__name'):
            if all(j not in i.getText() for j in List):         
                #print(i.getText())
                c = i.getText().split("(")[0].strip().title()
                courses.append(c)
                if "(IRE)" in i.getText():
                    loc = 'Ire'
                else:
                    loc = 'UK'
                
                if "(AW)" in i.getText():
                    surf = 'AW'
                else:
                    surf = 'Turf'

                self.meetings.append([c.title(), loc, surf])
                
        print(self.meetings)
                        
    def scrapeResults(self):
        data = {}
        raceday_resp = requests.get(self.raceday_url)
        raceday_content = raceday_resp.content
        soup = BS(raceday_resp.content, "html.parser")
        global df, dsr_df
        self.meetings = []
        List = [ '(ARG)', '(AUS)', '(BHR)','(BRZ)', '(CAN)', '(CHI)', '(CZE)', '(DEN)', '(FR)', '(GER)', '(HK)', 
                '(IND)', '(ITY)', '(JER)', '(JPN)', '(KOR)', '(KSA)', '(NOR)', '(NZ)', '(PER)', '(QA)', '(SAF)', '(SIN)',
                '(SPA)', '(SWE)', '(SWI)', '(TUR)', '(UAE)', '(URU)', '(USA)', 'SCOOP',
                'ABANDONED', '(ARAB)','Free', 'WORLDWIDE']
        racetypes = ['Chase', 'Hurdle', 'Flat Race', 'Bumper']
        jump_races = ['Hurdle', 'Chase']
 
        self.df = pd.DataFrame()
        for o,i in enumerate(soup.find_all('h2', class_= 'rp-raceCourse__row__name')):
            if all(j not in i.getText() for j in List):         
                #print(i.getText())
                c = i.getText().split("(")[0].strip()
                if "(IRE)" in i.getText():
                    loc = 'Ire'
                else:
                    loc = 'UK'
                print(c.title())
                deats = soup.find_all('div', class_ = 'rp-raceCourse__panel__details')
                if deats[o].find('span', class_= 'rp-raceCourse__panel__details__content__info__text').getText().strip() != None:
                    going = deats[o].find('span', class_= 'rp-raceCourse__panel__details__content__info__text').getText().strip()

                    if "Standard" in going:
                        surf = 'AW'
                    else:
                        surf = 'Turf'

                
                self.meetings.append([c.title(), loc, surf])
                print([c.title(), loc, surf, self._date])
                
                coursename = c.title()
                if c.title() in list(courses.keys()):
                    atr_course = courses[c.title()]
                else:
                    atr_course = c.title()

                for ele in soup.find_all(
                    attrs={"data-diffusion-coursename": c}
                ):
                    rtime = ele["data-diffusion-racetime"].replace(":", "")
                    print(rtime)
                    if 'Abandoned' not in ele.getText() and 'Void' not in ele.getText():
                        race_response = requests.get(f"https://racingpost.com{ele['href']}")
                        soup2 = BS(race_response.content, "html.parser")
                        #print(race_response.status_code, "rp")
                        atr_response = requests.get(f'https://www.attheraces.com/racecard/{atr_course}/{self._date.strftime("%d-%B-%Y")}/{rtime}', headers = headerProxy.chromeHeader)
                        #print(atr_response.status_code,"atr")

                        while int(atr_response.status_code) != 200:
                            print(f"Recieved {r}: Sleeping for 2s and retrying.")
                            time.sleep(2)
                            atr_response = requests.get(f'https://www.attheraces.com/racecard/{atr_course}/{self._date.strftime("%d-%B-%Y")}/{rtime}', headers = headerProxy.chromeHeader)

                        soup_atr = BS(atr_response.content, "html.parser")
                        #print(soup_atr.find_all('p', class_= 'p--medium'))#[1].getText().strip())
                        going_atr = soup_atr.find_all('p', class_= 'p--medium')[1].getText().strip()

                        if soup2.find('span', class_ = 'rp-raceTimeCourseName_condition') != None:
                            going = soup2.find('span', class_ = 'rp-raceTimeCourseName_condition').getText().strip()
                                                        
                            if "Standard" in going:
                                surf = 'AW'
                            else:
                                surf = 'Turf'

                        if c.title() == 'Lingfield' and surf == 'AW':
                            coursename = 'Lingfield AW'

                        ####void race check
                        # if 'Void' in soup2.find('div', class_='rp-raceCourse__panel__race__info__smallDetails').getText():
                        #     print(soup2.find('div', class_='rp-raceCourse__panel__race__info__smallDetails'))
                        title = soup2.find('h2', class_ = 'rp-raceTimeCourseName__title').getText().strip()
                            
                        
                        if soup2.find('span', class_='rp-raceTimeCourseName_distanceFull') == None:
                            dist = soup2.find('span', class_='rp-raceTimeCourseName_distance').getText().strip()
                            dist_y, dist_f = intY(dist)
                            
                        else:    
                            dist = soup2.find('span', class_='rp-raceTimeCourseName_distanceFull').getText().strip().replace('(',"").replace(')',"")
                            dist_y, dist_f = intY(dist)
                        
                        rbage = soup2.find('span', class_ = 'rp-raceTimeCourseName_ratingBandAndAgesAllowed')
                        
                        if rbage != None:
                            rbage = rbage.getText().strip().split()
                                                    
                        if rbage != None:
                            if len(rbage) == 2: 
                                rb = int(rbage[0].split("-")[1].replace(",",""))
                                agebr = rbage[1].strip().replace("(","").replace(")","")
                            else:
                                rb = np.nan
                                agebr = rbage[0].strip()
                        else:
                            agebr = np.nan
                            rb = np.nan
                        
                        if soup2.find('span', class_ = 'rp-raceTimeCourseName_class') != None:
                            cl = int(soup2.find('span', class_ = 'rp-raceTimeCourseName_class').getText().strip().replace(")","")[-1])
                        else:
                            cl = np.nan
                        
                        title = soup2.find('h2', class_= 'rp-raceTimeCourseName__title').getText()
                        if any(i in title for i in racetypes):
                            code = 'NH'
                        else:
                            code = 'Flat'

                        ###This section creates a few variables for data analysis later on.
                        race_type = np.nan
                        black_type = np.nan
                        if code == 'Flat':
                            if "Handicap" in title:
                                race_type = 'Handicap'
                            elif "Nursery" in title:
                                race_type = "Nursery"
                            elif "Maiden" in title:
                                race_type = "Maiden"
                            elif "Novice" in title:
                                race_type = "Novice"
                            elif "Claiming" in title:
                                race_type = "Claiming"
                            elif "Selling" in title:
                                race_type = "Selling"
                            elif "Conditions Stakes" in title:
                                race_type = "Conditions Stakes"

                        if code == 'Flat':
                            if "Group 1" in title:
                                race_type = 'Group 1'
                            elif "Group 2" in title:
                                race_type = "Group 2"
                            elif "Group 3" in title:
                                race_type = "Group 3"
                            elif "Listed" in title:
                                race_type = "Listed"
                       
                        
                        if race_type in ['Handicap', 'Nursery']:
                            hcp = 'Yes'
                        else:
                            hcp = 'No'
                       
                        ##Lps is here, there is some tricky ones with the full descriptions, so will have to scrape the more precise ATR going.
                        # if c.title() == 'Southwell' and surf == 'AW' and code == 'NH':
                        #     LPS = 4 
                        # elif c.title() == 'Southwell' and surf == 'AW' and code == 'Flat':
                        #     LPS = 5 
                        # else:
                        #     LPS = lps[code][going]
 
                        # if any(i in title for i in jump_races):
                        if soup2.find('span', class_= 'rp-raceTimeCourseName_hurdles') != None:
                            jumps = int(soup2.find('span', class_= 'rp-raceTimeCourseName_hurdles').getText().strip().split(" ")[0])
                        else:
                            jumps = np.nan
                        #print(jumps)
                        if not np.isnan(jumps):
                            #print('here')
                            code = 'NH'
                        
                        runners = int(soup2.find_all('span', class_ = "rp-raceInfo__value")[0].getText().strip().split(" ")[0])
                        
                        ri = soup2.find_all('span', class_ = "rp-raceInfo__value")[2]                    
                        if set(ri.text.strip()).issuperset(set("slow by")):
                            a = ri.getText().replace("(", "").replace(")", "").split("slow")[-1]
                            t = ri.getText().replace("(", "").replace(")", "").split("slow")[0]
                            final_time_delta = "slow " + a.strip()
                            if len(a.split()) == 2:
                                win_delta = float(a.strip().split("by")[-1].replace("s",""))      
                            else: 
                                a = a.strip().split("by")[-1].replace("s","")
                                m = float(a.split()[0].replace('m',''))*60                         
                                s = float(a.split()[1].replace('s',''))
                                win_delta = +(m+s)
                        
                        elif set(ri.text.strip()).issuperset(set("fast by")):
                            a = ri.getText().replace("(", "").replace(")", "").split("fast")[-1]
                            t = ri.getText().replace("(", "").replace(")", "").split("fast")[0]
                            final_time_delta = "fast " + a.strip()
                            if len(a.split()) == 2:
                                win_delta = -float(a.strip().split("by")[-1].replace("s",""))      
                            else: 
                                a = a.strip().split("by")[-1].replace("s","")
                                m = float(a.split()[0].replace('m',''))*60
                                s = float(a.split()[1].replace('s',''))
                                win_delta = -(m+s)
                        ##cathches when there is no standard time such as bumpers fro jumpers
                        else:
                            win_delta = np.nan
                            t = ri.getText().replace("(", "").replace(")", "").split("slow")[0]
                            
                        winning_time_string = t
                        winning_time_list = winning_time_string.split()
                        seconds_per_unit = {"s": 1, "m": 60}
                        if len(winning_time_list) != 2:
                            if "m" in winning_time_list[0]:
                                winning_time_list.append("0s")
                            if "s" in winning_time_list[0]:
                                winning_time_list.insert(0, "0m")
                            final_min = winning_time_list[0]
                            final_sec = winning_time_list[1]
                            # final_min, final_sec = winning_time_list
                        
                        else:
                            final_min, final_sec = winning_time_string.split()
                        
                        final_time = (float(final_min[:-1]) * seconds_per_unit[final_min[-1]]) + (
                            float(final_sec[:-1]) * seconds_per_unit[final_sec[-1]]
                        )
                                                
                        win_time = round(final_time,2)
                        
                        for l,k in enumerate(soup2.find_all('tr', class_= 'rp-horseTable__mainRow')):
                            lst = []
                            # for i in k.find_all('a'):
                            #     print(i.prettify())
                            # print('gap')
                            # content = attrs
                            
                            train = k.find('a', {"data-test-selector" : "link-trainerName"}).getText().strip()
                            joc = k.find('a', {"data-test-selector" : "link-jockeyName"}).getText().strip()
                            name = k.find('a', {"data-test-selector" : "link-horseName"}).getText().strip()
                            
                            if len(k.find_all('sup')) > 2:
                                claim = int(k.find_all('sup')[1].getText().strip())
                            else:
                                claim = 0
                            sp = k.find('span', class_= 'rp-horseTable__horse__price')

                            sp = k.find('span', class_= 'rp-horseTable__horse__price').getText().strip()

                            sp = sp.replace("c", "").replace("F", "").replace("J", "").replace("C", "").split("/")

                            if sp[0] == 'Evens' or sp[0] == 'Evs':
                                sp = 2.0
                            elif sp[0] == "":
                                sp = np.nan
                            else:   
                                sp = round(float(int(sp[0]) / int(sp[1])), 2) + 1.0

                            #to do 
                                #put in catches for non finishers make PU = 250 or something. 
                            d = k.find('div', class_= 'rp-horseTable__pos__numWrapper').getText().strip().replace('\xa0','').split("\n")
    
                            positions = ['PU', 'F', 'UR', 'R', 'BD', 'REF', 'RO', 'DSQ', 'SU', 'RR', 'CO', 'LFT']
                            pos = d[0].split('(')[0] 
                            
                            if pos in positions:    
                                pos = 0
                            else:
                                pos = int(pos)
                            
                            if len(d[0].split('(')) == 2:
                                draw = int(d[0].split('(')[1].replace(')',""))         
                            else:
                                draw = 0
                            
                            ####this sets pu and other non finsihers as 0 lenghts behind the winner, would rather its a nan, do this by setting  pu 251, and F to 252 etc.
                            ##if len(d) == 1 and pos > 200 dist to  win = np.nan

                            if len(d) > 1 and len(d) == 4:
                                dist_win = d[-1].replace('[',"").replace(']',"")
                                dist_hif = d[-1]
                            if len(d) > 1 and len(d) == 5:
                                dist_win = d[-1].replace('[',"").replace(']',"")
                                dist_hif = d[-2]
                            
                            s_keys = set(conversions.fract_char_to_float.keys())
                    
                            s_tokens = set(conversions.tokens.keys())
                            
                            if len(d) == 1 and pos != 0:
                                dist_win = 0
                                dist_hif = 0
    
                            if len(d) == 1 and pos == 0:
                                dist_win = 0
                                dist_hif = 0

                            
                            if dist_win != 0:
                                decimal_sum = 0 
                                if len(dist_win) > 1:
                                    f = set(dist_win).intersection(s_keys)
                                    if f:
                                        for i, num in enumerate(dist_win[:-1]):
                                            decimal_sum += int(num) * 10 ** (len(dist_win[:-1]) - 1 - i)
                                        dist_win = float(decimal_sum) + conversions.fract_char_to_float[f.pop()]
                                        
                                    else:
                                        f = set([dist_win]).intersection(s_tokens)
                                        if f:
                                            # print("Intersection")
                                            dist_win = conversions.tokens[f.pop()]
                                        else:
                                            # for i, num in enumerate(dist_win[:-1]):
                                            #     decimal_sum += int(num) * 10 ** (len(dist_win[:-1]) - 1 - i)
                                            # dist_win = float(decimal_sum)
                                            dist_win = float(dist_win)

                                elif len(dist_win) == 1 and len(dist_win) != 0:
                                    # print("Intersection l=1: ", set(datum).intersection(s_keys))
                                    f = set(dist_win).intersection(s_keys)
                                    g = set([dist_win]).intersection(s_tokens)
                                    if f:
                                        # print("Intersection")
                                        dist_win = conversions.fract_char_to_float[f.pop()]
                    
                                    
                                    elif g:
                                        # print("Intersection")
                                        dist_win = conversions.tokens[f.pop()]
                    
                                    elif dist_win == "0":
                                        dist_win = 0
                    
                                    else:
                                        # print(datum, "No intersection")
                                        dist_win = float(dist_win)
    
                            if dist_hif != 0:
                                decimal_sum = 0 
                                if len(dist_hif) > 1:
                                    f = set(dist_hif).intersection(s_keys)
                                    if f:
                                        for i, num in enumerate(dist_hif[:-1]):
                                            decimal_sum += int(num) * 10 ** (len(dist_hif[:-1]) - 1 - i)
                    
                                        dist_hif = float(decimal_sum) + conversions.fract_char_to_float[f.pop()]
                                        
                                    else:
                                        f = set([dist_hif]).intersection(s_tokens)
                                        if f:
                                            # print("Intersection")
                                            dist_hif = conversions.tokens[f.pop()]
                    
                                        else:
                                            # for i, num in enumerate(dist_hif[:-1]):
                                            #     decimal_sum += int(num) * 10 ** (len(dist_hif[:-1]) - 1 - i)
                                            dist_hif = float(dist_hif)
                    
                                elif len(dist_hif) == 1 and len(dist_hif) != 0:
                                    # print("Intersection l=1: ", set(datum).intersection(s_keys))
                                    f = set(dist_hif).intersection(s_keys)
                                    g = set([dist_hif]).intersection(s_tokens)
                                    if f:
                                        # print("Intersection")
                                        dist_hif = conversions.fract_char_to_float[f.pop()]
                    
                                    
                                    elif g:
                                        # print("Intersection")
                                        dist_hif = conversions.tokens[f.pop()]
                    
                                    elif dist_hif == "0":
                                        dist_hif = 0
                    
                                    else:
                                        # print(datum, "No intersection")
                                        dist_hif = float(dist_hif)
    
                            if len(d) == 1 and pos == 0:
                                dist_win = np.nan
                                dist_hif = np.nan
                            w = []
                            for m in k.find('td', class_ = 'rp-horseTable__spanNarrow rp-horseTable__wgt').find_all('span')[0:2]:
                                w.append(m.getText().strip())
                            st = int(w[0])
                            lbs = int(w[1])
                            
                            weight = st*14 + lbs
                            
                            age = int(k.find('td', class_ = 'rp-horseTable__spanNarrow rp-horseTable__spanNarrow_age').getText().strip())
                            
                            if len(k.find('td', class_ = 'rp-horseTable__spanNarrow rp-horseTable__wgt').getText().strip().split("\n")) > 1:
                                hg = k.find('td', class_ = 'rp-horseTable__spanNarrow rp-horseTable__wgt').getText().strip().split("\n")[-1].strip()
                            else:
                                hg = None
                            
                            _or = k.find_all('td', class_ = 'rp-horseTable__spanNarrow')[2].getText().strip()
                            
                            if _or == '–':
                                _or = 0
                            else:
                                _or = int(_or)
                            
                            #l is in line with the main row. it comes from enumarting the for loop along with k.
                            ped = soup2.find_all('tr', class_= 'rp-horseTable__pedigreeRow')[l]
                                
                            parents = ped.find_all('a', class_ = "ui-profileLink ui-link ui-link_table js-popupLink")
                            genc = ped.find('td', colspan = "11").getText().strip().split(" ")
                            colour = genc[0].strip()
                            gender = genc[1].strip()
                            sire = parents[0].getText().split("(")[0].strip()
                            dam = parents[1].getText().split("(")[0].strip()

                            meeting_id = str(self._date).replace("-","_") + "_" + c.title()
                            race_id = str(self._date).replace("-","_") + "_" + c.title() + "_" + rtime
                            
                            ###This section creates a few variables for data analysis later on.
                            rns_btn = round((runners - pos)/(runners -1),4)
                            rns_btn_sq = round(rns_btn **2,4)
                            
                                
                            
                            data = {'course': coursename,
                                    'date': str(self._date).replace("-","_"),
                                    'adv_dist_f': dist_f,
                                    'adv_dist_y': dist_y,
                                    'going': going,
                                    'going_atr': going_atr,
                                    'race_time': rtime,
                                    'name': name,
                                    'l_name': name.lower(),
                                    'jockey': joc,
                                    'joc_claim': claim,
                                    'trainer': train,
                                    'pos': pos,
                                    'rns_btn': rns_btn,
                                    'rns_btn_sq': rns_btn_sq,
                                    'draw': draw,
                                    'weight_lbs': weight,
                                    'or': _or,
                                    'd_hif': dist_hif,
                                    'd_win': dist_win,
                                    'age': age,
                                    'headgear': hg,
                                    'sp_dec': sp,
                                    'class': cl,
                                    'win_time': win_time,
                                    'win_time_delta': win_delta,
                                    'sire': sire,
                                    'dam': dam,
                                    "colour": colour,
                                    "gender": gender,
                                    'meeting_id' : meeting_id,
                                    'race_id' : race_id,
                                    'surf': surf,
                                    'code': code,
                                    'title': title,
                                    'black_type': black_type,
                                    'race_type': race_type,
                                    'hcp':hcp,
                                    'runners': runners,
                                    'r_band': rb,
                                    'age_group': agebr,
                                    'jumps': jumps#,
                                    #'lps':LPS
                                    }
                            self.df = self.df.append(data, ignore_index=True)
#        df = self.df
        
        #LPS calculater here, dont have this automated yet.
        # if df.shape[0] > 0:
        #     df['est_time'] = round(df['d_win']/ df['lps'] + df['win_time'],2) 
        #     df['est_time_delta'] = round(df['d_win']/ df['lps'] + df['win_time_delta'],2) 

#        self.df = df
        
        if data != {}:
            col = list(data.keys())
            col.append('dsr')
            
            rm2 = pd.DataFrame()
            d = {}
            dsr_df = pd.DataFrame()
            for i in self.meetings:
                print(i)            
                #spliting rail movements for now, can pull the meeting Ids and plug them into the scraper directly 
                # if i[1] == 'UK' and i[2] == "Turf":
                #     rm = BhaScraper(course = i[0], rday = self).data()
                #     rm2 = rm2.append(rm)
    
                if i[0] in list(courses.keys()):
                    i[0] = courses[i[0]]
                print(i[0])
                    
                atr_url = f'https://www.attheraces.com/racecards/{i[0]}/{self._date.strftime("%d-%B-%Y")}'
                print(atr_url)
                raceday_resp = requests.get(atr_url,headers = headerProxy.chromeHeader)
                raceday_content = raceday_resp.content
                soup = BS(raceday_resp.content, "html.parser")
                           
                
                for h in soup.find_all("div", class_="card-entry"):
                    if h.find("span", class_ = 'p--x-small visible--inline-block tooltip') != None:
                       dsr = h.find("span", class_ = 'p--x-small visible--inline-block tooltip').getText().strip()
                       if "(" in dsr:
                           if dsr.split("(")[0].strip() == '' :
                               dsr = 0
                           else:
                               dsr = int(dsr.split("(")[0].strip())
                       else:
                           dsr = int(dsr)                  
                    else:
                       dsr = 0
                    name = h.find("a", class_="horse__link").getText().split("\r\n")[1].strip()
                    d = {'name':name,
                         'l_name': name.lower(),
                         'dsr':dsr
                        }
                    dsr_df = dsr_df.append(d,ignore_index=True)
    
            #spliting rail movements for now, can pull the meeting Ids and plug them into the scraper directly
            # if rm2.shape[0] > 0 and df.shape[0] > 0:          
            #     self.df = self.df.merge(rm2.drop(columns = {'meeting_id'}), on = 'race_id', how = 'left')
            
            self.df = self.df.merge(dsr_df.drop(columns = 'name'), on= ['l_name'], how = 'left' , indicator = True)         
            self.df = self.df.reindex(columns = col)
        
        
    def splitData(self):
        if self.df.shape[0] > 0:
            df = self.df
            flt = df.loc[df['code'] == 'Flat'].drop(columns = {'jumps'})
            nh = df.loc[df['code'] == 'NH'].drop(columns = {'draw'})
            ####can put these 2 dfs in seperate places.
            print(self._date)
            nh.to_csv(f"G:/My Drive\horse_racing/scraped_data/Basic/nh/{self._date}_NH.csv", index = False)
            flt.to_csv(f"G:/My Drive\horse_racing/scraped_data/Basic/Flat/{self._date}_Flat.csv", index = False)
            

            ##below 2 functions and for loop generate grpahs in a folder automatically for flat meeting draws.
            def stats_basic(df, groupby = 'trainer_name', runners = 5, file = None):
                data = pd.DataFrame()
                rns_btn = df.groupby(groupby)['rns_btn_sq'].agg({'size','mean'}).rename(columns = {'size':'count', 'mean':'rns_btn_sq'})
                rns_btn = rns_btn.loc[rns_btn['count'] > 0]
                rns_btn = round(rns_btn[['count', 'rns_btn_sq']],3)

                return rns_btn

            def meet(df):
                print(df.shape)
                course = df['course'].drop_duplicates().iloc[0]
                date = df['date'].drop_duplicates().iloc[0]
    
                draw_stats = stats_basic(df, 'draw')
                        
                lm = sns.lmplot(data = draw_stats.reset_index(), x = 'draw', y = 'rns_btn_sq')
                fig = lm.fig     
                fig.suptitle(f"draw_{course}_{date}", fontsize=12)    
                fig.savefig(f"G:/My Drive/horse_racing/draw_graphs/{date}_{course}_draw.png")
                # plt.savefig(f"C:/Users/kirwans/OneDrive - Paddy Power Betfair/Workbook/data/graphs/{date}_{meeting}_epf.png")

        
            for i in flt['course'].unique():
                meeting = flt.loc[flt['course'] == i]
                print(meeting.shape)
                meet(meeting)
        
        
    ###Timeforms service has fixed this.
    # def pcolumns(self):
    #     if self._date == date.today() + datetime.timedelta(days =1):
    #         self.preraceday_url = f"https://www.racingpost.com/racecards/tomorrow"
    #     else:
    #         self.preraceday_url = f"https://www.racingpost.com/racecards/{self._date}"
        
        
            

#r.scrapeResults()
# for j in range(1,30):
#     for i in range(4,13):
#         r = RaceDay(j,i,2020)
#         # r.scrapeCourses()
#         r.scrapeResults()


from datetime import date, timedelta

# start_date = date(2023, 7, 14)
# end_date = date(2023, 7, 16)
# delta = timedelta(days=1)
# while start_date <= end_date:

#     r = RaceDay(start_date.day,start_date.month,start_date.year)
#     #r.scrapeCourses()
#     r.scrapeResults()
#     r.splitData()
#     start_date += delta



start_date = date(2023, 5, 27)
end_date = date(2023, 7, 13)
delta = timedelta(days=1)
while start_date <= end_date:

    r = RaceDay(start_date.day,start_date.month,start_date.year)
    #r.scrapeCourses()
    r.scrapeResults()
    r.splitData()
    start_date += delta


# test  = r.df.merge(dsr_df.drop(columns = 'name'), on= ['l_name'], how = 'left' , indicator = True)
# test['_merge'].value_counts()
# bad = test.loc[test['_merge'] == 'left_only']