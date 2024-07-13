import pandas as pd
import glob
from matplotlib import pyplot as plt
import seaborn as sns


def bdata():
    #temp = pd.DataFrame()
    temp = pd.read_csv('C:/Racing_Data/scraped_data/Basic/Combined - Copy.csv')
    for f in glob.glob("C:/Racing_Data/scraped_data/Basic/Flat/*")[-104:]:       
        df = pd.read_csv(f)
        print(f)
        #df = pd.concat(df, ignore_index=True)
        temp = temp.append(df, ignore_index=True)
        #temp = temp.loc[temp['surf'] == 'AW']
        temp.to_csv('C:/Racing_Data/scraped_data/Basic/Combined.csv', index = False)

def tdata():
    temp = pd.DataFrame()
    for f in glob.glob("C:/Racing_Data/scraped_data/New_TPD_meetings/*"):       
        df = pd.read_csv(f)
        print(f)
        #df = pd.concat(df, ignore_index=True)
        temp = temp.append(df, ignore_index=True)
        #temp = temp.loc[temp['surf'] == 'AW']
        temp.to_csv('C:/Racing_Data/scraped_data/NewTPD.csv', index = False)

def sData():
    temp = pd.DataFrame()
    for f in glob.glob("C:/Racing_Data/Sales/mares/*"):       
        df = pd.read_csv(f)
        if 'november' in f:
            df = df.rename(columns = {'Year' : 'Year Foaled'})
        print(f)
        #df = pd.concat(df, ignore_index=True)
        temp = temp.append(df, ignore_index=True)
        #temp = temp.loc[temp['surf'] == 'AW']
    temp['name'] = temp['Name'].str.split("(").str[0].str.strip()
    ###need to be deadly careful with the below line
    temp['price'] = temp['Price'] + temp['price_euros']
    temp['age'] = temp['year'] - temp['Year Foaled']
    temp.to_csv('C:/Racing_Data/Sales/maresAll.csv', index = False)
        

def getTData():
    global data
    data = pd.read_csv('C:/Racing_Data/scraped_data/NewTPD.csv')
    data = data.loc[data['course'] != 'Southwell']
    data = data.loc[(data['fs%'] >= 93) & data['fs%']
                      & (data['mean_stride_freq'] >= 2)
                      & (data['mean_stride_length'] >= 21)]    
       
def fsf(course,dist):
    global df
    df = data.loc[(data['dist_f'] == dist) & (data['course'] == course)
                  & (data['fs%'] >= 93) & data['fs%']
                  & (data['mean_stride_freq'] >= 2)]
    plt.scatter(df['fs%'], df['mean_stride_freq'])
    #mnF = data.groupby('dist_f_r')['mean_stride_freq']. 

def rnsf(course,dist,hcp = 'yes'):
    global df
    df = data.loc[(data['dist_f'] == dist) & (data['course'] == course)]
    #               & (data['fs%'] >= 93) & data['fs%']
    #               & (data['mean_stride_freq'] >= 2)
    #               & (data['mean_stride_length'] >= 21)]
    if hcp == 'yes':
        df = df.loc[df['race_type'] == 'Handicap']
    
    if hcp == 'nov':
        nov = ['Novice', 'Maiden']
        df = df.loc[df['race_type'].isin(nov)]    
        
    plt.scatter(df['mean_stride_length'], df['%rns_btn'])
    #mnF = data.groupby('dist_f_r')['mean_stride_freq']. 

def dist(course):
    df = data.loc[data['course'] == course]
    print(df['dist_f'].unique())
    
def mnF():
    global mnf
    mnf = data.groupby('dist_f_r')['mean_stride_freq'].mean()
    #looks reliable enough considering small sample at points
    
def siref(sire):
    global smnf
    df = data.loc[data['sire'] == sire]
    smnf = df.groupby('dist_f_r')['mean_stride_freq'].mean()
    

def getBData():   
    global b_data
    
def maxor():
    global ors
    b_data = pd.read_csv('C:/Racing_Data/scraped_data/Basic/Combined.csv')
    gender  = ['f','m']    
    b_data = b_data.loc[b_data['gender'].isin(gender)]
    ors = b_data.groupby('name')['or'].max()
    ors = ors.reset_index()
    ors.to_csv('C:/Racing_Data/Sales/maresors.csv')
    
    
def getSData():
    global s_data
    s_data = pd.read_csv('C:/Racing_Data/Sales/maresAll.csv')
    
def ormer():
    getSData()
    #maxor()
    s_data = s_data.merge(ors, on = 'name', how = 'left')
    
    