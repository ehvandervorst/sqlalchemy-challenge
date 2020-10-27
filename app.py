import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measure = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

#Home page. List all routes that are available.
@app.route("/")
def home():
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
    # Convert the query results to a dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.
    session = Session(engine)

    results = session.query(Measure.date, Measure.prcp).filter(func.strftime("%Y-%m-%d", Measure.date) >= "2016-08-23").order_by(Measure.date).all()
    session.close()

    # Convert list of tuples into normal list
    year_prcp = []
    for date, prcp in results:
        year_dict = {}
        year_dict[date] = prcp
        year_prcp.append(year_dict)

    return jsonify(year_prcp)

@app.route("/api/v1.0/stations")
def stations():
    # Return a JSON list of stations from the dataset.
    session = Session(engine)
    stations = session.query(Station.name, Station.station, Station.latitude, Station.longitude, Station.elevation).all()
    session.close()
    all_stations = []
    for name, station, latitude, longitude, elevation in stations:
        station_dict={}
        station_dict["name"] = name
        station_dict["station"] = station
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        all_stations.append(station_dict)
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    #Query the dates and temperature observations of the most active station for the last year of data.
    #Return a JSON list of temperature observations (TOBS) for the previous year.
    session = Session(engine)
    temp = session.query(Measure.tobs).filter(func.strftime("%Y-%m-%d", Measure.date) >= "2016-08-23").filter(Measure.station == 'USC00519281').all()
    session.close()
    year_temp = list(np.ravel(temp))

    return jsonify(year_temp)

@app.route("/api/v1.0/start")
def start():
    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-endrange.
    #When given the start only, calculate TMIN, TAVG and TMAX for all dates greater than and equal to the start date.
    session = Session(engine)
    stemp = session.query(func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs), Measure.date).filter(func.strftime("%Y-%m-%d", Measure.date) >= "2016-08-23").group_by(Measure.date).all()
    session.close()
        
    start_temp = []
    for min, avg, max, date in stemp:
        temp_dict={}
        temp_dict["date"] = date
        temp_dict["min"] = min
        temp_dict["average"] = avg
        temp_dict["max"] = max
        start_temp.append(temp_dict)
    return jsonify(start_temp)


@app.route("/api/v1.0/start/end")
def startend():
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

    session = Session(engine)
    setemp = session.query(func.min(Measure.tobs), func.avg(Measure.tobs), func.max(Measure.tobs), Measure.date).filter(func.strftime("%Y-%m-%d", Measure.date) >= "2015-08-23").filter(func.strftime("%Y-%m-%d", Measure.date) <= "2016-08-23").group_by(Measure.date).all()
    session.close()
        
    startend_temp = []
    for min, avg, max, date in setemp:
        setemp_dict={}
        setemp_dict["date"] = date
        setemp_dict["min"] = min
        setemp_dict["average"] = avg
        setemp_dict["max"] = max
        startend_temp.append(setemp_dict)
    return jsonify(startend_temp)

if __name__ == "__main__":
    app.run(debug=True)





