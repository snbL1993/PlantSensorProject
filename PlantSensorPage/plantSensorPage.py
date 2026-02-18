import json
import os
import plotly
import plotly.express as px
import pandas
from datetime import datetime, timedelta
import sqlalchemy
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

#read credentials from environment variables so they are not hardcoded in source
DB_HOST = os.environ.get('DB_HOST', '192.168.178.60')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'test_sensor')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'database')

#create engine once at startup so the connection pool is reused across requests
engine = sqlalchemy.create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

PLANT_NAMES = {
    '5c:85:7e:12:e2:b3': 'Bogenhanf',
    '5c:85:7e:12:e3:d3': 'Ficus Ginseng',
    '5c:85:7e:12:e4:f7': 'Aloe',
    '5c:85:7e:12:dc:f6': 'Monstera',
}

def databaseread(table: str):
    #using sqlalchemy to read from postgres database
    query = 'select * from {}'
    data = None
    try:
        data = pandas.read_sql(query.format(table), con=engine)

    except Exception as e:
        print(f"Could not read from database: {e}")

    return data

ALLOWED_DAYS = {1, 3, 7, 14}

def createPlotly(whichData: str, days: int):
    data = databaseread("sensor_data")
    if data is None:
        return jsonify(message='Could not read from database', graph=None), 500

    data['timeofdata'] = pandas.to_datetime(data['timeofdata'])
    cutoff = datetime.now() - timedelta(days=days)
    data = data[data['timeofdata'] >= cutoff]

    #naming plants in plot
    data['mac_address'] = data['mac_address'].replace(PLANT_NAMES)
    
    #create a Plotly figure
    figOne = px.line(
        data,
        x='timeofdata',
        y=whichData, 
        color='mac_address',
        title=f"{whichData} Test", 
        markers=True
        )
    
    #convert the figure to JSON
    graphOneJson = json.dumps(figOne, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(message=f'{whichData} data plotted successfully', graph=graphOneJson)

def get_days_param():
    days = request.args.get('days', 14, type=int)
    if days not in ALLOWED_DAYS:
        days = 14
    return days

@app.route('/')
def index():
    return render_template('index.html')

# API endpoint for Buttons
@app.route('/button1', methods=['POST'])
def button1():
    return createPlotly('moisture', get_days_param())


@app.route('/button2', methods=['POST'])
def button2():
    return createPlotly('light', get_days_param())


@app.route('/button3', methods=['POST'])
def button3():
    return createPlotly('temperature', get_days_param())


@app.route('/button4', methods=['POST'])
def button4():
    return createPlotly('conductivity', get_days_param())


@app.route('/button5', methods=['POST'])
def button5():
    return createPlotly('battery', get_days_param())






@app.route('/status', methods=['GET'])
def status():
    data = databaseread("sensor_data")
    if data is None:
        return jsonify(warnings=['Could not reach database']), 500

    data['timeofdata'] = pandas.to_datetime(data['timeofdata'])
    cutoff = datetime.now() - timedelta(hours=24)
    last_seen = data.groupby('mac_address')['timeofdata'].max()

    warnings = []
    for mac, name in PLANT_NAMES.items():
        if mac not in last_seen.index:
            warnings.append(f"{name}: no data found in database")
        elif last_seen[mac] < cutoff:
            hours_ago = int((datetime.now() - last_seen[mac]) / timedelta(hours=1))
            warnings.append(f"{name}: last reported {hours_ago}h ago — battery may be dead")

    return jsonify(warnings=warnings)


if __name__ == '__main__':
    
    app.run(threaded=True, use_reloader=False)