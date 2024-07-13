import pandas as pd
#function that creates a DF column for meeting ID and Race ID) 
# this is a weird one builf for an old dataset, idea is good but wil have to modified for our scraper. dont think it will be used.
def get_meeting_id(data, column = None, course = None, RaceTime = None):
    if column != None:
        Date = data[column]
    else:
        Date = data['Race Date']
    
    if course != None:
        Course = data[course]
    else:
        Course = data['Course']
 
    if RaceTime != None:
        RaceTime = data[RaceTime]
    else:
        RaceTime = data['Race Time']
    
    data['meeting_id'] = ""
    data['race_id'] = ""
    
    for k, (i,j,l) in enumerate(zip(Date,Course,RaceTime)):
        yr = i[-4:]
        mth = i[3:5]
        dy = i[0:2]
        
        meeting_id = yr + "_" + mth + "_" + dy + "_" + j
        race_id = yr + "_" + mth + "_" + dy + "_" + j + "_" + l
        data['meeting_id'].iloc[k] = meeting_id
        data['race_id'].iloc[k] = race_id
        #print(meeting_id)
    
    return data
    
    
    
        