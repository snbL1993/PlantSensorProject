import json
import plotly
import plotly.express as px
import pandas
from datetime import datetime, timedelta
import sqlalchemy
from flask import Flask, render_template, jsonify

app = Flask(__name__)

def databaseread(table: str):
    #engine=psycopg2.connect(
    #    host="192.168.178.60",
    #    port= 5432,
    #    database="test_sensor",
    #    user="postgres",
    #    password="database"
    #    )
    
    #using sqlalchemy to read from postgres database
    engine= sqlalchemy.create_engine('postgresql://postgres:database@192.168.178.60:5432/test_sensor')
    query = 'select * from {}'
    try:
        data = pandas.read_sql(query.format(table), con=engine)
        
    except:
        print("Could not read from database")
    
    return data

def createPlotly(whichData :str):
    data = databaseread("sensor_data")

    #only show last 4 weeks
    #ToDo: Make adjustable
    data['timeofdata'] = pandas.to_datetime(data['timeofdata'])
    cutoff = datetime.now() - timedelta(weeks=4)
    data = data[data['timeofdata'] >= cutoff]

    #naming plants in plot
    data['mac_address'] = data['mac_address'].replace({
        '5c:85:7e:12:e2:b3' : 'Bogenhanf', 
        '5c:85:7e:12:e3:d3' : 'Ficus Ginseng', 
        '5c:85:7e:12:e4:f7' : 'Aloe', 
        '5c:85:7e:12:dc:f6' : 'Monstera'
        })
    
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

#actions for buttons

def actionOne():
    plot = createPlotly('moisture')
    return plot

def actionTwo():
    plot = createPlotly('light')
    return plot

def actionThree():
    plot = createPlotly('temperature')
    return plot

def actionFour():
    plot = createPlotly('conductivity')
    return plot

def actionFive():
    plot = createPlotly('battery')
    return plot

@app.route('/')
def index():
    

    # Pass the JSON to the template
    return render_template('index.html')

# API endpoint for Buttons
@app.route('/button1', methods=['POST'])
def button1():
    graphJson = actionOne()
    return graphJson


@app.route('/button2', methods=['POST'])
def button2():
    graphJson = actionTwo()
    return graphJson


@app.route('/button3', methods=['POST'])
def button3():
    graphJson = actionThree()
    return graphJson


@app.route('/button4', methods=['POST'])
def button4():
    graphJson = actionFour()
    return graphJson


@app.route('/button5', methods=['POST'])
def button5():
    graphJson = actionFive()
    return graphJson






if __name__ == '__main__':
    
    app.run(threaded=True, use_reloader=False)