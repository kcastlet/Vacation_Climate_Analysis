# /api/v1.0/precipitation
# /api/v1.0/stations
# /api/v1.0/tobs
# /api/v1.0/<start> where start is a date in YYYY-MM-DD format
# /api/v1.0/<start>/<end> where start and end are dates in YYYY-MM-DD format

from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

import numpy as np

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect database into new model
Base = automap_base()
#Reflect tables
Base.prepare(engine, reflect=True)

#Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create session to connect to database 
session = Session(engine)

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

# Flask
app = Flask(__name__)


# Create routes
@app.route("/")
def greeting():
    return """
    Welcome to the API for Hawaii's climate.
    Available endpoints: <br>
    /api/v1.0/precipitation <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/&lt;start&gt; where start is a date in YYYY-MM-DD format <br> 
    /api/v1.0/&lt;start&gt;/&lt;end&gt; where start and end are dates in YYYY-MM-DD format
    """


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