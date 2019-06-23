# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import numpy as np
import pandas as pd
#reviews = pd.read_csv("ECDC_Dengue.csv")
from sqlalchemy import create_engine

#import files with disease data
#data was downloaded from European Centre for Disease Prevention and Control (ecdc)
Dengue = pd.read_csv("ECDC_Dengue.csv")
Malaria = pd.read_csv("ECDC_Malaria.csv")
Tick_enc = pd.read_csv("ECDC_Tick_enc.csv")

diseases_names=["Malaria", "Dengue", "Tick_enc"]
diseases=[Malaria, Dengue, Tick_enc]
years=[2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]

#make list with all countries represented in the disease data
countries_total=Dengue.loc[:,"RegionName"]
countries_unique=countries_total.drop_duplicates()
countries=countries_unique.tolist()

#filter for incidence rate, only use confirmed cases
def filter(disease):
    disease_filter = (disease["Indicator"] == "Notification rate") & (disease["Unit"] == "N/100000") & ((disease["Population"] == "All cases") | (disease["Population"] == "Confirmed cases"))
    return disease[disease_filter]

col_names = ['year', 'country'] + diseases_names
df_all = pd.DataFrame(columns=col_names)

list_all =[]

#arrange data
for year in years:
    for country in countries:
        
        temp_row_dict = {'year': year,'country':country}
    
        i=0
        for disease_name in diseases_names: 
            
            filtered_disease=filter(diseases[i])
            found_value = filtered_disease.loc[(filtered_disease['Time'] == year)&(filtered_disease['RegionName']==country),"NumValue"]
            if(found_value.size):
                temp_row_dict[disease_name] = found_value.values[0]
            i = i + 1
        list_all.append(temp_row_dict)
        
        
df_all = pd.DataFrame(list_all)
df_all_final=df_all.replace({'-': np.nan})

#produce an Engine object based on a URL, upload data to PostgreSQL
db = create_engine('postgres://mxzlpwli:RfRTVZpDm1V1QrOsk-lfJndPbBXE07T7@baasu.db.elephantsql.com:5432/mxzlpwli')
df_all_final.to_sql('Disease_table', db, if_exists='replace')
db.dispose()
