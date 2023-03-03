import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify

# Generate Engine to the Sqlite File
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# Reflect the Database Schema
Base = automap_base()
Base.prepare(engine, reflect=True)

# Saving references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Database Initiation
app = Flask(__name__)

# Initial Variables Used 
last_day = dt.date(2017, 8, 23)
one_year_back = last_day - dt.timedelta(days=365)

# Flask Routes
@app.route('/')
def home():
    return(
        '<style type="text/css">'
        'body {'
            'background-color: #DCF;'
            'font-family: Arial, sans-serif;'
            'text-align: center;'
        '}'
        '.display {'
            'font-size: 24px;'
            'color: #230;'
        '}'
        '#test:hover {'
            'color: #FFF;'
        '}'
        'a {'
            'color: #00F;'
        '}'
        'a:hover {'
            'color: #C0F;'
        '}'
        '</style>'
        f'<h1>Welcome to the Climate Analysis API!</h1>'
        f'<h2>These are the Available Routes:</h2>'
        f'<div class=display><a href=/api/v1.0/precipitation>/api/v1.0/precipitation</a></div><br/>'
        f'<div class=display><a href=/api/v1.0/stations>/api/v1.0/stations</a></div><br/>'
        f'<div class=display><a href=/api/v1.0/tobs>/api/v1.0/tobs</a></div><br/><br/>'
        f'<h3>For These Last Two Routes, You May Parse in a Start Date . . .</h3>'
        f'<h4>. . . or BOTH a Start Date AND an End Date</h4>'
        f'<div class=display id=hover>/api/v1.0/YYYY-MM-DD</div><br/>'
        f'<div class=display>/api/v1.0/YYYY-MM-DD/YYYY-MM-DD</div><br/>'
    )

@app.route('/api/v1.0/precipitation')
def precipitation():

    session = Session(engine)

    # Querying Measurement and Sorting to Make it More Readable
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_back).\
        order_by(Measurement.date).all()
    
    # Closing Session
    session.close()

    # Creating a Dictionary for Each Row of Data and Appending to List
    prcp_list = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict['date'] = date
        prcp_dict['precipitation'] = prcp
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)

@app.route('/api/v1.0/stations')
def stations():

    session = Session(engine)

    # Query for ALL Stations
    results = session.query(Station.name).all()

    session.close()

    # Converting List
    station_names = list(np.ravel(results))

    return jsonify(station_names)

@app.route('/api/v1.0/tobs')
def tobs():

    session = Session(engine)

    # Query Stations
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_back).\
        order_by(Measurement.date).all()

    session.close()

    # Converting List
    station_temps = list(np.ravel(results))

    return jsonify(station_temps)

@app.route('/api/v1.0/<start_date>')
def calc_temp_start(start_date):

    # In Route, the User Inputs the start_date in ISO 8601 format YYYY-MM-DD

    session = Session(engine)

    # Querying Measurement for Temperatures on and after start_date,
    # Then calculating min, max and avg
    results = session.query(func.min(Measurement.tobs), 
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    calc_list = []
    for tmin, tavg, tmax in results:
        instance_dict = {}
        instance_dict['Tmin'] = tmin
        instance_dict['Tavg'] = tavg
        instance_dict['Tmax'] = tmax
        calc_list.append(instance_dict)

    return jsonify(calc_list)

@app.route('/api/v1.0/<start_date>/<end_date>')
def calc_temp_start_end(start_date, end_date):

    # In Route, the User Inputs both the start_date & end_date in ISO 8601 format YYYY-MM-DD
    session = Session(engine)

    # Querying Measurement for Temperatures between start_date and end_date,
    # Then calculating min, max and avg like above
    results = session.query(func.min(Measurement.tobs),
                            func.avg(Measurement.tobs),
                            func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()

    session.close()

    calc_bound_list = []
    for tmin, tavg, tmax in results:
        bound_inst_dict = {}
        bound_inst_dict['Tmin'] = tmin
        bound_inst_dict['Tavg'] = tavg
        bound_inst_dict['Tmax'] = tmax
        calc_bound_list.append(bound_inst_dict)

    return jsonify(calc_bound_list)

if __name__ == '__main__':
    app.run(debug=True)
