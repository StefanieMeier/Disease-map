#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 17:45:06 2019

@author: stemeier

This script imports the raw datasets of historically measured climate data 
that was downloaded from the EU Copernicus Earth Observation Programme:
https://cds.climate.copernicus.eu/cdsapp#!/search?type=dataset
The data is then filtered and organized in a pandas dataframe and finally
stored in a remote PostgreSQL database. 
"""

#import netCDF4 since the raw data comes in this format which can only be read
#with this package
import netCDF4

#import pandas and numpy for data manipulation
import pandas as pd

#needed for database connection
from sqlalchemy import create_engine

#needed to specify timeframe of imported data
import datetime as dt

#function to find closest index to specified value
def near(array,value):
    idx=(abs(array-value)).argmin()
    return idx

#location of raw dataset
filename = "datasets/temp_europe.nc"

#netCDF4 takes care of the import of the .nc file
nc = netCDF4.Dataset(filename, 'r', Format='NETCDF4')

#extract all imported latitudes and longitudes
lat = nc.variables['lat'][:]
lon = nc.variables['lon'][:]

#extract all imported times
time_var = nc.variables['time']
dtime = netCDF4.num2date(time_var[:],time_var.units)

#specify the exact time period we want
start = dt.datetime(2008,1,1,0,0,0)
stop = dt.datetime(2017,12,1,0,0,0)

#find the nearest index of the start and stop time
istart = netCDF4.date2index(start,time_var,select='nearest')
istop = netCDF4.date2index(stop,time_var,select='nearest')

# specify the temperature data at 2m above sea level
vname = 't2m'
var = nc.variables[vname]

#filter the data for the correct time frame
hs = var[istart:istop,iy,ix]


#array with all relevant years listed for looping
years=[2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]

#make array with all time indices of January 1st at 12:00:00am in all specified years
iyears = []
for y in years:
    yi = dt.datetime(y,1,1,0,0,0)
    itime = netCDF4.date2index(yi,time_var,select='nearest')
    iyears.append(itime)

#prepare array that will contain all relevant data rows
list_all = []

#create array of row names for all years
row_names = list(['lon','lat'])
row_names.extend(list(map(str,years)))

#counting index in lonigtude loop
ilo = 0
for lo in lon:

    #counting index in latitude loop
    ila = 0
    for la in lat:
        
        #get data for all years at looped lat and lon
        hs = var[iyears,ila,ilo]
        
        #create row withh all temperature data and add lon and lat at the end
        row_values = list([lo,la])
        row_values.extend(hs.tolist())
        
        #make a dict from the row names and row values so it can be translated
        #easier to dataframe
        temp_row_dict = dict(zip(row_names, row_values))

        #add the formatted row to the row array
        list_all.append(temp_row_dict)
        
        #increase lat counting index
        ila = ila + 1
    #increase lon counting index
    ilo = ilo + 1

#convert row array to dataframe
df_all = pd.DataFrame(list_all)

#open remote database connection
db = create_engine('postgres://[hidden_username:hidden_password]@baasu.db.elephantsql.com:5432/[hidden_username]')

#write data to database
df_all.to_sql('Temperature_table', db, if_exists='replace')

#close db connection
db.dispose()