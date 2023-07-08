# Import the dependencies.
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all the available api routes."""
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

#Convert the query results from precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)

    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= one_year_ago).filter(Measurement.prcp != None).\
    order_by(Measurement.date).all()

    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

#Return a JSON list of stations from the dataset

@app.route("/api/v1.0/stations")
def stations():
    total_number_stations = session.query(Station).distinct().count()

    active_station_counts = session.query(Measurement.station, func.count(Measurement.station)).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).all()
    
    station_list = [result for result in active_station_counts]
    
    return jsonify(station_list)


#Query the dates and temperature observations of the most-active station for the previous year of data
#Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    one_year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)

    year_temp = session.query(Measurement.tobs).\
            filter(Measurement.date >= one_year_ago).filter(Measurement.station == 'USC00519281').\
            order_by(Measurement.tobs).all()
    
    temperature_list = [temp for temp in year_temp]

    return jsonify(temperature_list)

#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/<start>")
def temp_start(start):

    # Query the minimum, average, and maximum temperatures for all dates greater than or equal to the start date
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
     # Create a dictionary to hold the temperature statistics
    temp_dict = {
        "TMIN": temp_stats[0][0],
        "TAVG": temp_stats[0][1],
        "TMAX": temp_stats[0][2]
    }

    return jsonify(temp_dict)

@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):

    # Query the minimum, average, and maximum temperatures for the dates between the start and end dates (inclusive)
    temp_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()
    
    # Create a dictionary to hold the temperature statistics
    temp_dict = {
        "TMIN": temp_stats[0][0],
        "TAVG": temp_stats[0][1],
        "TMAX": temp_stats[0][2]
    }

    return jsonify(temp_dict)

if __name__ == '__main__':
    app.run(debug=True)