#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 21:17:50 2019

@author: stemeier

This flask web app simply represents a one-page web app that contains
a map visualizing the spread of diseases with chaning climate.
Many of the functions pull the pre-processed data from a remote PostgreSQL
database and convert it to json objects that are loaded by the d3.js script
wihtin the HTML template.
"""

#flask imports
from flask import Flask
from flask import render_template
from flask_cors import CORS, cross_origin

#sqlalchemy import for db connection
from sqlalchemy import create_engine

#import pandas for data conversion
import pandas as pd

#define the flask app
app = Flask(__name__)

#added these because of cross origin errors when connecting to the remote db server
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "*"}})


#load disease data (incidence rate per disease per country per year) from remote PostgreSQL db
@app.route("/getdiseasedata")
@cross_origin()
def get_diseases():

    #open database connection
    db = create_engine('postgres://[hidden_username:hidden_password]@baasu.db.elephantsql.com:5432/[hidden_username]')
    diseases = db.execute('SELECT * FROM "Disease_table"')
    
    #convert imported data to pandas dataframe
    df = pd.DataFrame(diseases.fetchall())
    df.columns = diseases.keys()

    #convert dataframe to json
    json_diseases = df.to_json(orient='records')

    #close the database connection
    db.dispose()
    return json_diseases

#load temperature data from remote PostgreSQL db
@app.route("/gettempdata")
@cross_origin()
def get_temperatures():

    #open database connection
    db = create_engine('postgres://[hidden_username:hidden_password]@baasu.db.elephantsql.com:5432/[hidden_username]')
    temps = db.execute('SELECT * FROM "Temperature_table"')
    
    #convert imported data to pandas dataframe
    df = pd.DataFrame(temps.fetchall())
    df.columns = temps.keys()

    #filter the data for area north of latitude 36deg 
    df_filter =  df['lat']>36
    df_filtered = df[df_filter]

    #convert dataframe to json
    json_temps = df_filtered.to_json(orient='records')

    #close the database connection
    db.dispose()
    return json_temps

#load average temperature data (average temperature per country per year) from remote db
@app.route("/getavgtempdata")
@cross_origin()
def get_avg_temperatures():

    #open database connection
    db = create_engine('postgres://[hidden_username:hidden_password]@baasu.db.elephantsql.com:5432/[hidden_username]')
    temps = db.execute('SELECT * FROM "Temperature_avg_table"')
    
    #convert imported data to pandas dataframe
    df = pd.DataFrame(temps.fetchall())
    df.columns = temps.keys()

    #convert dataframe to json
    json_avg_temps = df.to_json(orient='records')
    
    #json_temps_var = "temp_measurements={"+json_temps+"}"
    db.dispose()
    return json_avg_temps

#render the main disease map page 
@app.route("/")
@cross_origin()
def disease_map():
    return render_template("disease_map.html")

#start the server
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)