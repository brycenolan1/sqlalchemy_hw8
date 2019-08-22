import numpy as np
import pandas as pd

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func, extract, cast

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    sel = [Measurement.date, 
       func.sum(Measurement.prcp)]
    results = session.query(*sel).\
                filter(func.strftime('%Y', Measurement.date)).\
                filter(Measurement.date <= '2017-08-23').\
                filter(Measurement.date >= '2016-08-23').\
                group_by(Measurement.date).\
                order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    monthly_sum = []
    for date, prcp in results:
        monthly_sum_dict = {}
        monthly_sum_dict["date"] = date
        monthly_sum_dict["prcp_sum"] = prcp
        monthly_sum.append(monthly_sum_dict)

    return jsonify(monthly_sum)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Measurement.station, func.count(Measurement.tobs)).\
                group_by(Measurement.station).\
                order_by(func.count(Measurement.tobs).desc()).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).\
                filter(func.strftime('%m', Measurement.date)).\
                filter(Measurement.date <= '2017-08-23').\
                filter(Measurement.date >= '2016-08-23').\
                filter(Measurement.station == 'USC00519281').\
                order_by(Measurement.date).all()

    session.close()

    # Convert list of tuples into normal list
    tob_data = list(np.ravel(results))

    return jsonify(tob_data)


if __name__ == '__main__':
    app.run(debug=True)
