#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 12:32:38 2019

@author: stemeier

This script imports the raw datasets of disease data that was downloaded 
from the European Centre for Disease Prevention and Control (ecdc):
https://atlas.ecdc.europa.eu/public/index.aspx
The data is then filtered and organized in a pandas dataframe and finally
stored in a remote PostgreSQL database. 
"""

#import libraries for data manipulation and database communication
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

#import files with disease data
#data was downloaded from European Centre for Disease Prevention and Control (ecdc)
Dengue = pd.read_csv("datasets/ECDC_Dengue.csv")
Malaria = pd.read_csv("datasets/ECDC_Malaria.csv")
Tick_enc = pd.read_csv("datasets/ECDC_Tick_enc.csv")

#create array of all imported disease data
diseases=[Malaria, Dengue, Tick_enc]

#create arrays of column and row labels
diseases_names=["Malaria", "Dengue", "Tick_enc"]
years=[2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]


#make list with all countries represented in the disease data
countries_total=Dengue.loc[:,"RegionName"]
countries_unique=countries_total.drop_duplicates()
countries=countries_unique.tolist()

#filter function for incidence rate, only use confirmed cases
def filter(disease):
    disease_filter = (disease["Indicator"] == "Notification rate") & (disease["Unit"] == "N/100000") & ((disease["Population"] == "All cases") | (disease["Population"] == "Confirmed cases"))
    return disease[disease_filter]

#prepare dataframe to contain colums of year and country as well as all diseases
#then loop through years and countries and add them es rows
col_names = ['year', 'country'] + diseases_names
df_all = pd.DataFrame(columns=col_names)

#create array that will contain all rows
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
        
#write the rows to dataframe
df_all = pd.DataFrame(list_all)

#replace all "-" values as NaNs
df_all_final=df_all.replace({'-': np.nan})

#open remote database connection 
db = create_engine('postgres://[hidden_username:hidden_password]@baasu.db.elephantsql.com:5432/[hidden_username]')

#write dataframe to database
df_all_final.to_sql('Disease_table', db, if_exists='replace')

#close db connection
db.dispose()
