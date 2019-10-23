#import flask, sqlalchemy and other dependencies 
from flask import Flask,jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt

#create engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Map classes
ME = Base.classes.measurement
ST = Base.classes.station

#create app and pass name
app = Flask(__name__)

#definte info shown at index route
@app.route("/")
def home():
     return (
        f"Aloha! Welcome to the Hawaiian Weather API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"Please enter date as yyyy-mm-dd")

# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def prcp():
     session =  Session(engine)

     # Calculate the date 1 year ago from the last data point in the database
     year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

     # Perform a query to retrieve the data and precipitation scores
     precip = session.query(ME.date,ME.prcp).filter(ME.date >= year_ago).all()

     session.close

     rain_list =[]
     for date, prcp in precip:
         rain_dict={}
         rain_dict[date] = prcp
         rain_list.append(rain_dict)

     return jsonify(rain_list)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stn():
    session =  Session(engine)

    stn_count = session.query(ME.station,func.count(ME.station)).group_by(ME.station).order_by(func.count(ME.station).desc())

    session.close

    station_list = [station for station,count in stn_count]

    print("List of stations")

    return jsonify(station_list)

# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session =  Session(engine)

    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)

    temps = session.query(ME.tobs).filter(ME.date >= year_ago).all()

    session.close

    temp_list =list(np.ravel(temps))

    return jsonify(temp_list)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start_date>")
def start(start_date):
    session =  Session(engine)
    
    readings = session.query(func.min(ME.tobs),func.avg(ME.tobs),func.max(ME.tobs)).filter(ME.date >= start_date).first()

    session.close

    return jsonify(readings)

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date,end_date):
    session =  Session(engine)
    
    min_max = session.query(func.min(ME.tobs),func.avg(ME.tobs),func.max(ME.tobs)).filter(ME.date >= start_date,ME.date <= end_date).first()

    session.close

    return jsonify(min_max)

if __name__ == '__main__':
    app.run(debug=True)




    

