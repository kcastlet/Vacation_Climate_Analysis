# /api/v1.0/precipitation
# /api/v1.0/stations
# /api/v1.0/tobs
# /api/v1.0/<start> where start is a date in YYYY-MM-DD format
# /api/v1.0/<start>/<end> where start and end are dates in YYYY-MM-DD format

from flask import Flask, jsonify
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect database
Base = automap_base()
Base.prepare(engine, reflect=True)

# Connect to database 
session = Session(engine)
conn = engine.connect()

#Save classes to tables
measurement = Base.classes.measurement
station = Base.classes.station


def calc_temps(start_date, end_date):
    
    return session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

#Open Flask module
app = Flask(__name__)

#Match URLs to view functions in Flask
@app.route("/")
def home():
    return 'Welcome to the API for the climate in Hawaii.'
    'These links can be accessed:<br/>'.\
		   '<a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a><br/>'.\
		   '<a href="/api/v1.0/stations">/api/v1.0/stations</a><br/>'.\
		   '<a href="/api/v1.0/tobs">/api/v1.0/tobs</a><br/>'.\
		   '<a href="/api/v1.0/&lt;start&gt;">/api/v1.0/&lt;start&gt;</a><br/>'.\
		   '<a href="/api/v1.0/&lt;start&gt;/&lt;end&gt;">/api/v1.0/&lt;start&gt;/&lt;end&gt;</a>'

@app.route("/api/v1.0/precipitation")
def prcp():
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= "2016-08-23").\
    filter(measurement.date <= "2017-08-23").all()

    dict = []
    for row in results:
        date_dict = {}
        date_dict[row.date] = row.prcp
        dict.append(date_dict)

    return jsonify(dict)



@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()
    results_list = list(np.ravel(results))

    return jsonify(results_list)



@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(measurement.tobs).\
        filter(measurement.date >= "2016-08-23").\
        filter(measurement.date <= "2017-08-23").all()
    results_list = list(np.ravel(results))

    return jsonify(results_list)



@app.route("/api/v1.0/<start>")
def start_date(start):
    end_date = session.query(func.max(measurement.date)).all()[0][0]
    temps = calc_temps(start, end_date)
    temps_list = list(np.ravel(temps))

    return jsonify(temps_list)



@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    temps = calc_temps(start, end)
    temps_list = list(np.ravel(temps))

    return jsonify(temps_list)

if __name__ == '__main__':
    app.run(debug=True)