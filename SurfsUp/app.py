# Import the dependencies.

import sqlalchemy
import numpy as np
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask,jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB

#################################################
# Flask Setup
#################################################
app = Flask(__name__)
session = Session(engine)
#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return ("Welcome to my API <br/>"
           "The available routes are <br/>"
           "<a href=http://127.0.0.1:5000/api/v1.0/precipitation>Precipitation Data</a> <br/>"
           "<a href=http://127.0.0.1:5000/api/v1.0/stations>Stations</a> <br/>"
           "<a href=http://127.0.0.1:5000/api/v1.0/tobs>Observed Temperatures</a> <br/>"
           "To check a temperature from a date until the last available date: <br/>"
           "http://127.0.0.1:5000/api/v1.0/ and add the start date at the end <br/>"
           "To check a temperature from a start date until the end date add it it after the start date. <br/>"
           "The only format which is barred for dates is those containing '/' as they will break the url <br />"
           "For example: http://127.0.0.1:5000/api/v1.0/23-6-2017/23-7-2017"
           )

@app.route('/api/v1.0/precipitation')
def getprcp():
    mostrecent = session.query(Measurements.date).\
    order_by(Measurements.date.desc()).first()
    latestdate = pd.to_datetime(mostrecent[0])
    yearago = dt.date(latestdate.year-1,latestdate.month,latestdate.day)
    one_year_prcp = session.query(Measurements.date,Measurements.prcp).filter(Measurements.date >= yearago).order_by(Measurements.date).all()
    session.close()
    results = [dict(row) for row in one_year_prcp]
    return jsonify(results)
    
@app.route('/api/v1.0/stations')
def getstations():
    stationcount = session.query(Stations.station,Stations.name,Stations.latitude,Stations.longitude,Stations.elevation).all()
    stations = [dict(row) for row in stationcount]
    session.close()
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def gettobs():
    activestationid = (session.query(Measurements.station, 
    func.count(Measurements.station)).group_by(Measurements.station).\
    order_by(func.count(Measurements.station).desc()).first())[0]
    mostrecent = session.query(Measurements.date).\
    order_by(Measurements.date.desc()).first()
    latestdate = pd.to_datetime(mostrecent[0])
    yearago = dt.date(latestdate.year-1,latestdate.month,latestdate.day)
    one_year_tobs = session.query(Measurements.station, Measurements.date,Measurements.tobs).\
    filter(Measurements.date >= yearago).\
    filter(Measurements.station == activestationid).\
    order_by(Measurements.date).all()
    result = [dict(row) for row in one_year_tobs]
    session.close()
    return jsonify(result)

@app.route('/api/v1.0/<start>')
def getstart(start):
    start = pd.to_datetime(start)
    startdate = start.date()
    tobs_from_start = session.query(func.min(Measurements.tobs),func.max(Measurements.tobs),func.avg(Measurements.tobs)).\
    filter(Measurements.date >= startdate).\
    order_by(Measurements.date.asc()).all()
    session.close()
    result = [list(row) for row in tobs_from_start]
    return jsonify(result[0])

@app.route('/api/v1.0/<start>/<end>')
def getstart_end(start,end):
    start = pd.to_datetime(start)
    startdate = start.date()
    end = pd.to_datetime(end)
    enddate = end.date()
    tobs_til_end = session.query(func.min(Measurements.tobs),func.max(Measurements.tobs),func.avg(Measurements.tobs)).\
    filter(Measurements.date >= startdate).\
    filter(Measurements.date <= enddate).\
    order_by(Measurements.date.asc()).all()
    session.close()
    result = [list(row) for row in tobs_til_end]
    return jsonify(result[0])

if __name__ == '__main__':
    app.run(debug=True)