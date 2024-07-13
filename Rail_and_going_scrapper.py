import requests
import headerProxy
from bs4 import BeautifulSoup as BS
from bs4 import Comment
import pandas as pd
import datetime

def getRail(day):
       
    if day == 0:
        day = ""
        date = datetime.date.today()
        l = -1
    
    elif day == 1:
        day = 'tomorrow'
        date = datetime.date.today() + datetime.timedelta(days=1)
        l = -1
        
    elif day == 2:
        date = datetime.date.today() + datetime.timedelta(days= day)
        day = date
        l = -1

        
    url_RP = f'https://www.racingpost.com/racecards/{day}'
    r = requests.get(url_RP, headers = headerProxy.chromeHeader)
    
    print(r.status_code)
    print(url_RP)
    soup = BS(r.content, "html.parser")
    List = ['(AUS)', '(HK)', '(UAE)', '(FR)' ,'(USA)', 'Free', 'Worldwide']
    temp = {}
    data = pd.DataFrame()
    for i in soup.find_all('section')[:l]:
        # if "(" not in i.find('div', class_ = 'RC-accordion__courseInfo').getText():         
        if all(j not in i.find('div', class_ = 'RC-accordion__courseInfo').getText() for j in List):         
            # print('Spaceer /n /n')
           
            # print(i.find('div', class_= 'RC-courseDescription__info'), "NEW")        
            # print(i.find('div', class_ = 'RC-accordion__courseInfo').getText().split('(')[0].strip())
            temp = {'course' : i.find('div', class_ = 'RC-accordion__courseInfo').getText().split('(')[0].strip(),
                    'rail_going' : i.find('div', class_= 'RC-courseDescription__info').getText().strip()
                    }
            print(temp)
            data = data.append(temp, ignore_index=True)
            
    data['date'] = date
    data['meeting_id'] = str(date).replace('-', '_') + '_' + data["course"]

    data.to_csv(f"C:/racing-web-scraper/Data/scraped_data/Rail_movements/{date}_RM.csv", index = False)
    return data