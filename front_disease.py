#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 22 21:17:50 2019

@author: stemeier
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 12:14:28 2018

@author: stemeier
"""

from flask import Flask
from flask import render_template
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine
import pandas as pd


app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/*": {"origins": "*"}})



#disease map page 
#load disease data (incidence rate per disease per country per year) from PostgreSQL
@app.route("/getdiseasedata")
@cross_origin()
def get_diseases():
    db = create_engine('postgres://mxzlpwli:RfRTVZpDm1V1QrOsk-lfJndPbBXE07T7@baasu.db.elephantsql.com:5432/mxzlpwli')
    diseases = db.execute('SELECT * FROM "Disease_table"')
    
    df = pd.DataFrame(diseases.fetchall())
    df.columns = diseases.keys()

    json_diseases = df.to_json(orient='records')
    db.dispose()
    return json_diseases

#load temperature data from PostgreSQL
@app.route("/gettempdata")
@cross_origin()
def get_temperatures():
    db = create_engine('postgres://mxzlpwli:RfRTVZpDm1V1QrOsk-lfJndPbBXE07T7@baasu.db.elephantsql.com:5432/mxzlpwli')
    temps = db.execute('SELECT * FROM "Temperature_table"')
    
    df = pd.DataFrame(temps.fetchall())
    df.columns = temps.keys()
    df_filter =  df['lat']>36
    df_filtered = df[df_filter]

    json_temps = df_filtered.to_json(orient='records')
    #json_temps_var = "temp_measurements={"+json_temps+"}"
    db.dispose()
    return json_temps

#load average temperature data (average temperature per country per year) from PostgreSQL@app.route("/getavgtempdata")
@app.route("/getavgtempdata")
@cross_origin()
def get_avg_temperatures():
    db = create_engine('postgres://mxzlpwli:RfRTVZpDm1V1QrOsk-lfJndPbBXE07T7@baasu.db.elephantsql.com:5432/mxzlpwli')
    temps = db.execute('SELECT * FROM "Temperature_avg_table"')
    
    df = pd.DataFrame(temps.fetchall())
    df.columns = temps.keys()

    json_avg_temps = df.to_json(orient='records')
    #json_temps_var = "temp_measurements={"+json_temps+"}"
    db.dispose()
    return json_avg_temps


@app.route("/")
@cross_origin()
def disease_map():
    return render_template("disease_map.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)