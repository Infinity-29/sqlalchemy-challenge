import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measure = Base.classes.measurement
stn = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the database for dates and precipitation
    results = session.query(measure.date, measure.prcp)

    data = []

    for date, prcp in results:
        dict = {}
        dict[date] = prcp
        data.append(dict)

    #Return a json dictionary of date and precipitation

    session.close() 
    
    return jsonify(data)

# Station
@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    station_data = {}

    station_results = session.query(stn.station,stn.name).all()

    for x, y in station_results:
        station_data[x] = y

    #Return a JSON list of stations from the dataset.

    session.close() 
    
    return jsonify(station_data)

# tobs
# Query the dates and temperature observations of the most active station for the last year of data.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results = session.query(measure.date,  measure.tobs,measure.prcp).filter(measure.date >= '2016-08-23').filter(measure.station=='USC00519281').order_by(measure.date).all()

    # Convert the list to Dictionary
    all_tobs = []
    for prcp, date,tobs in results:
        tobs_dict = {}
        tobs_dict["prcp"] = prcp
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        
        all_tobs.append(tobs_dict)

    session.close()

    return jsonify(all_tobs)

# start
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
    

    start_date_list = []

    fin_results =session.query(measure.date,func.min(measure.tobs), func.avg(measure.tobs), 
    func.max(measure.tobs).filter(measure.date >= start)).group_by(measure.date).all()

    for date ,min, avg, max in fin_results:
        start_date_var = {}
        start_date_var["Date"] = date
        start_date_var["TMIN"] = min
        start_date_var["TAVG"] = avg
        start_date_var["TMAX"] = max
        start_date_list.append(start_date_var) 

        session.close()
    return jsonify(start_date_list)

# start.end
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of min, avg and max tobs for start and end dates"""

    start_end_temp_obs = []

    Final_results = session.query(func.min(measure.tobs), func.avg(measure.tobs), func.max(measure.tobs).filter(measure.date >= start).filter(measure.date <= end)).all()

    # Create a dictionary from the row data and append to a list of start_end_date_tobs
  
    for finmin, finavg, finmax in Final_results:
        start_end_temp_obs_dict = {}
        start_end_temp_obs_dict["Start Date"] = start
        start_end_temp_obs_dict["End Date"] = end
        start_end_temp_obs_dict["TMIN"] = finmin
        start_end_temp_obs_dict["TAVG"] = finavg
        start_end_temp_obs_dict["TMAX"] = finmax
        start_end_temp_obs.append(start_end_temp_obs_dict) 
    
        session.close()
    return jsonify(start_end_temp_obs)

if __name__ == '__main__':
    app.run(debug=True)
