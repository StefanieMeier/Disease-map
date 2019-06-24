# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 13:54:42 2019

@author: stemeier

This script takes the temperature map data from the database and first 
bins it into the individual countries by reverse geo-coding the coordinates 
into country names and then averages it for years. This avergage temperature
for every country and year was needed to plot the 2D line graphs of disease
occurance correlation with temperature over time.
"""

#needed for db communication
from sqlalchemy import create_engine

#needed for data manipulation
import pandas as pd

#needed for geocoding
from geopy.geocoders import Nominatim

#open database connection and get temperature data
db = create_engine('postgres://[hidden_username:hidden_password]@baasu.db.elephantsql.com:5432/[hidden_username]')
temps = db.execute('SELECT * FROM "Temperature_table"')

#convert temperature data to dataframe
df = pd.DataFrame(temps.fetchall())
df.columns = temps.keys()

#filter temperature map to locations north of latitude 36deg and also exclude rows that contain nan's
df_filter =  df['lat']>36
df_filtered = df[df_filter]
new_df = df_filtered.dropna()

#create a geolocator object with random user_agent
geolocator = Nominatim(user_agent="mano_hano")

# function to return country name for every location (row)
def find_country(row):
    pos = str(row['lat']) + ', ' + str(row['lon'])
    print(pos)
    try:
        location = geolocator.reverse(pos, timeout = 60, language='en')
        print(location.raw['address']['country'])
        return location.raw['address']['country']
    except:
        return None

#implement a rate limiter to not exceed the geo coding API used
from geopy.extra.rate_limiter import RateLimiter
geocode = RateLimiter(find_country, min_delay_seconds=1)

#this process takes quite long so we want to see the time estimation for pandas processing
from tqdm import tqdm
tqdm.pandas()

#do the geo coding and add a new column with the country name for every row
new_df["country"] = new_df.progress_apply(geocode, axis=1)

#calculate the mean temperature for all rows grouped by countries
grouped_df = new_df.groupby(['country']).mean()

#delete the columns that are not needed
del grouped_df['lon']
del grouped_df['lat']
del grouped_df['index']

#write the final dataframe to the database
grouped_df.to_sql('Temperature_avg_table', db, if_exists='replace')

#close the database connection
db.dispose()

