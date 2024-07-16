import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from flask import Flask, jsonify
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of precipitation data for the last 12 months."""
    session = Session(engine)
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    last_date = pd.to_datetime(most_recent_date)
    one_year_ago = last_date - timedelta(days=365)
    one_year_ago = one_year_ago.strftime('%Y-%m-%d')
    
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()

    # Convert list of tuples into normal list
    stations = list(np.ravel(results))

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""
    session = Session(engine)
    most_recent_date = session.query(measurement.date).order_by(measurement.date.desc()).first()[0]
    last_date = pd.to_datetime(most_recent_date)
    one_year_ago = last_date - timedelta(days=365)
    one_year_ago = one_year_ago.strftime('%Y-%m-%d')
    
    # Find the most active station
    active_station = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()[0]
    
    # Query the temperature observations
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == active_station).\
        filter(measurement.date >= one_year_ago).all()
    
    session.close()

    # Convert list of tuples into normal list
    temp_data = list(np.ravel(results))

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start date."""
    session = Session(engine)
    print(f"Start date: {start}")
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= "2015-03-30").all()
    print(f"Query results: {results}")
    session.close()

    # Convert list of tuples into normal list
    temp_stats = list(np.ravel(results))

    return jsonify(temp_stats)


@app.route("/api/v1.0/<start>/<end>")
def temp_stats_start_end(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given date range."""
    session = Session(engine)
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= "2015-03-30").\
        filter(measurement.date <= "2016-06-28").all()
    
    session.close()

    # Convert list of tuples into normal list
    temp_stats = list(np.ravel(results))

    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)