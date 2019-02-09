import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-8-22<br/>"
        f"/api/v1.0/2016-8-22/2016-9-22<br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Quering to retrieve the precipitation data and date 
    prcp_date = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date).all()

    dic = {i[0]:i[1] for i in prcp_date}
    session.close()
    return jsonify(dic)
        

@app.route("/api/v1.0/stations")
def stations():
    # Listing all the station and there frequency
    stations = session.query(Measurement.station).group_by(Measurement.station).all()
    stations = [i[0] for i in stations]
    session.close()
    return "Available Stations: \n {}".format(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    #Querying last one year of temperature.
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    
    year_ago = last_date - dt.timedelta(days=366)
    tobs_date = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= year_ago).order_by(Measurement.date.desc()).all()
    tobs = {i[0]:i[1] for i in tobs_date}
    session.close()
    return jsonify(tobs)
    return "Temperature Observed from {} to {}: <br/> {}".format(last_date,year_ago,tobs)

@app.route("/api/v1.0/<startdate>")
def startdate(startdate):
    #list of the minimum temperature, the average temperature, and the max temperature for a given start date.
    startdate = dt.datetime.strptime(startdate, '%Y-%m-%d')
    output = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= startdate).all()
    session.close()
    return "Temparetur from the {} to the latest date is as below <br/> Minimum Tempareture: {} <br/> Maximum Tempareture: {} <br/> Average Tempareture: {} ".format(startdate,output[0][0],output[0][1],output[0][2])

@app.route("/api/v1.0/<startdate>/<enddate>")
def startenddate(startdate,enddate):
    #list of the minimum temperature, the average temperature, and the max temperature for a given start-end range.
    startdate = dt.datetime.strptime(startdate, '%Y-%m-%d')
    enddate = dt.datetime.strptime(enddate, '%Y-%m-%d')
    output = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= startdate).filter(Measurement.date <= enddate).all()
    session.close()
    return "Temparetur from {} to {} is as below <br/> Minimum Tempareture: {} <br/> Maximum Tempareture: {} <br/> Average Tempareture: {} ".format(startdate,enddate,output[0][0],output[0][1],output[0][2])

if __name__ == '__main__':
    app.run(debug=True)


