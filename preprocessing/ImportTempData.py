#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  2 17:45:06 2019

@author: stemeier
"""

import netCDF4
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
from scipy import interpolate
from sqlalchemy import create_engine

filename = "data/temp_europe.nc"

nc = netCDF4.Dataset(filename, 'r', Format='NETCDF4')
print(nc.variables.keys())

lat = nc.variables['lat'][:]
lon = nc.variables['lon'][:]
time_var = nc.variables['time']
dtime = netCDF4.num2date(time_var[:],time_var.units)

# determine what longitude convention is being used [-180,180], [0,360]
print(lat.min(),lat.max())

# find closest index to specified value
def near(array,value):
    idx=(abs(array-value)).argmin()
    return idx


# specify some location to extract time series
lati = 47.22; loni = 8.33  # Georges Bank

# Find nearest point to desired location (could also interpolate, but more work)
ix = near(lon, loni)
iy = near(lat, lati)


# Extract desired times.      
# 1. Select -+some days around the current time:
#start = dt.datetime.utcnow()- dt.timedelta(days=3)
#stop = dt.datetime.utcnow()+ dt.timedelta(days=3)
#       OR
# 2. Specify the exact time period you want:
start = dt.datetime(2008,6,2,0,0,0)
stop = dt.datetime(2015,6,3,0,0,0)

istart = netCDF4.date2index(start,time_var,select='nearest')
istop = netCDF4.date2index(stop,time_var,select='nearest')
print(istart,istop)

# Get all time records of variable [vname] at indices [iy,ix]
vname = 't2m'
#vname = 'surf_el'
var = nc.variables[vname]
hs = var[istart:istop,iy,ix]
tim = dtime[istart:istop]


# Create Pandas time series object
ts = pd.Series(hs,index=tim,name=vname)

## Use Pandas time series plot method
#ts.plot(figsize=(12,4),
#   title='Location: Lon=%.2f, Lat=%.2f' % ( lon[ix], lat[iy]),legend=True)
#plt.ylabel(var.units);


coordinate_grid_lon = np.linspace(-33,64,num=100)
coordinate_grid_lat = np.linspace(36,70,num=100)

start = dt.datetime(2008,1,1,0,0,0)
stop = dt.datetime(2017,12,1,0,0,0)

years=[2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017]
iyears = []

for y in years:
    yi = dt.datetime(y,1,1,0,0,0)
    itime = netCDF4.date2index(yi,time_var,select='nearest')
    iyears.append(itime)

istart = netCDF4.date2index(start,time_var,select='nearest')
istop = netCDF4.date2index(stop,time_var,select='nearest')
tim = dtime[istart:istop]

list_all = []

ilo = 0


for lo in lon:
    ila = 0
    for la in lat:
        
        hs = var[iyears,ila,ilo]
        
        row_names = list(['lon','lat'])
        row_names.extend(list(map(str,years)))
        
        row_values = list([lo,la])
        row_values.extend(hs.tolist())
        
        temp_row_dict = dict(zip(row_names, row_values))
        
#        for y in years:
#            print(lo,la,y)
#            yi = dt.datetime(y,1,1,0,0,0)
#            itime = netCDF4.date2index(yi,time_var,select='nearest')
#            temp_row_dict[y] = var[itime,la,lo].tolist()
        

        print(temp_row_dict)
        list_all.append(temp_row_dict)
        
        ila = ila + 1
        
    ilo = ilo + 1
        

print('Done with loops')

df_all = pd.DataFrame(list_all)
print('Done with panda conversion..')

db = create_engine('postgres://mxzlpwli:RfRTVZpDm1V1QrOsk-lfJndPbBXE07T7@baasu.db.elephantsql.com:5432/mxzlpwli')
print('Done with db connection..')

df_all.to_sql('Temperature_table', db, if_exists='replace')
db.dispose()