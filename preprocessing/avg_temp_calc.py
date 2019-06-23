# -*- coding: utf-8 -*-
"""
Created on Sun Jun 16 13:54:42 2019

@author: Max
"""

from flask import Flask
from flask import render_template
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
import json

from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="mano_hano")

db = create_engine('postgres://mxzlpwli:RfRTVZpDm1V1QrOsk-lfJndPbBXE07T7@baasu.db.elephantsql.com:5432/mxzlpwli')
temps = db.execute('SELECT * FROM "Temperature_table"')

df = pd.DataFrame(temps.fetchall())
df.columns = temps.keys()

df_filter =  df['lat']>36
df_filtered = df[df_filter]
new_df = df_filtered.dropna()

def find_country(row):
    pos = str(row['lat']) + ', ' + str(row['lon'])
    print(pos)
    try:
        location = geolocator.reverse(pos, timeout = 60, language='en')
        print(location.raw['address']['country'])
        return location.raw['address']['country']
    except:
        return None

from geopy.extra.rate_limiter import RateLimiter
geocode = RateLimiter(find_country, min_delay_seconds=1)

from tqdm import tqdm
tqdm.pandas()


new_df["country"] = new_df.progress_apply(geocode, axis=1)

grouped_df = new_df.groupby(['country']).mean()
del grouped_df['lon']
del grouped_df['lat']
del grouped_df['index']
grouped_df.to_sql('Temperature_avg_table', db, if_exists='replace')

