# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

#################################################
# Database Setup
#################################################

# connect to database
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create and bind session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

# Display the available routes on the landing page
@app.route("/")
def home():
    return(
        f"<center><h2>Welcome to the Hawaii Climate Analysis Local API!</h2></center>"
        f"<center><h3>Please select from one of the available routes</h3></center>"
        f"<center>/api/v1.0/precipitation</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start/end</center>"
    )

#################################################
# Flask Routes
#################################################

# /api/v1.0/precipitation route - set up route for precipiitation scores
@app.route("/api/v1.0/precipitation")
def precip():
    # return the previous year's precipitation as a json
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #previousYear

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previousYear).all()
    session.close()
    #dictionary with the date as the key and the precipitation (prcp) as the value
    # make list comprehension where fill in all of the dates
    precipitation = {date: prcp for date, prcp in results}
    # convert to a json
    return jsonify(precipitation)

# /api/v1.0/stations route - set up route for station names 
@app.route("/api/v1.0/stations")
def stations():
    # show a list of all the stations in the database
    # Perform a query to retrieve the names of the stations
    results = session.query(Station.station).all()
    session.close()

    #use numpy to convert to array, and then a list
    stationList = list(np.ravel(results))
    #convert to json and display
    return jsonify(stationList)

# /api/v1.0/tobs route - set up route for temperature observations
@app.route("/api/v1.0/tobs")
def temperatures():
    # return the previous year temperatures for the most active station 'USC00519281'
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #previousYear

    # Perform a query to retrieve the temperature from the most active station from the past year 
    results = session.query(Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= previousYear).all()
    
    session.close()

    #use numpy to convert to array, and then a list
    temperaturelist = list(np.ravel(results))
    #return the list of temperatures and display
    return jsonify(temperaturelist)

# /api/v1.0/start/end and /api/v1.0/start routes 
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None): 
    
    # return the min, max, and avg temperatures calculated from the given start date to the given date for the start and end parameters
    #selection statement
    selection = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    
    #if no end date is specified, grab all dates after start
    if not end: 
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*selection).filter(Measurement.date >= startDate).all()
        session.close()

        #use numpy to convert to array, and then a list
        temperaturelist = list(np.ravel(results))
        #return the list of temperatures and display
        return jsonify(temperaturelist)

    #otherwise grab all results within range specified
    else:
        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")
        results = session.query(*selection)\
            .filter(Measurement.date >= startDate, )\
            .filter(Measurement.date <= endDate, ).all()
        session.close()

        #use numpy to convert to array, and then a list
        temperaturelist = list(np.ravel(results))
        #return the list of temperatures and display
        return jsonify(temperaturelist)


##app launcher
if __name__ == '__main__':
    app.run(debug=True)

