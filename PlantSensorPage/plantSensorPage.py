import json
import plotly
import plotly.express as px
import pandas
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
    
    engine= sqlalchemy.create_engine('postgresql://postgres:database@192.168.178.60:5432/test_sensor')
    query = 'select * from {}'
    try:
        df = pandas.read_sql(query.format(table), con=engine)
        
    except:
        print("Could not read from database")
    
    return df

def createPlotly(whichData :str):
    dfOne = databaseread("sensor_data")
    dfOne['mac_address'] = dfOne['mac_address'].replace({'5c:85:7e:12:e2:b3' : 'Bogenhanf', '5c:85:7e:12:e3:d3' : 'Rosablätter'})
    # Create a Plotly figure
    figOne = px.line(dfOne, x='timeofdata', y=whichData, color='mac_address',
                     title=f"{whichData} Test", markers=True)
    
    # Convert the figure to JSON
    graphOneJson = json.dumps(figOne, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(message=f'{whichData} data plotted successfully', graph=graphOneJson)

def actionOne():
    plot = createPlotly('moisture')
    return plot

def actionTwo():
    whichData = 'light'
    dfOne = databaseread("sensor_data")
    dfOne['mac_address'] = dfOne['mac_address'].replace({'5c:85:7e:12:e2:b3' : 'Bogenhanf', '5c:85:7e:12:e3:d3' : 'Rosablätter'})
    # Create a Plotly figure
    figOne = px.line(dfOne, x='timeofdata', y=whichData, color='mac_address',
                     title="Light Test", markers=True)
    
    # Convert the figure to JSON
    graphOneJson = json.dumps(figOne, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(message='Light data plotted successfully', graph=graphOneJson)

def actionThree():
    whichData = 'temperature'
    dfOne = databaseread("sensor_data")
    dfOne['mac_address'] = dfOne['mac_address'].replace({'5c:85:7e:12:e2:b3' : 'Bogenhanf', '5c:85:7e:12:e3:d3' : 'Rosablätter'})
    # Create a Plotly figure
    figOne = px.line(dfOne, x='timeofdata', y=whichData, color='mac_address',
                     title="Temperature Test", markers=True)
    
    # Convert the figure to JSON
    graphOneJson = json.dumps(figOne, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(message='Temperature data plotted successfully', graph=graphOneJson)

def actionFour():
    whichData = 'conductivity'
    dfOne = databaseread("sensor_data")
    dfOne['mac_address'] = dfOne['mac_address'].replace({'5c:85:7e:12:e2:b3' : 'Bogenhanf', '5c:85:7e:12:e3:d3' : 'Rosablätter'})
    # Create a Plotly figure
    figOne = px.line(dfOne, x='timeofdata', y=whichData, color='mac_address',
                     title="Conductivity Test", markers=True)
    
    # Convert the figure to JSON
    graphOneJson = json.dumps(figOne, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(message='Conductivity data plotted successfully', graph=graphOneJson)

def actionFive():
    whichData = 'battery'
    dfOne = databaseread("sensor_data")
    dfOne['mac_address'] = dfOne['mac_address'].replace({'5c:85:7e:12:e2:b3' : 'Bogenhanf', '5c:85:7e:12:e3:d3' : 'Rosablätter'})
    # Create a Plotly figure
    figOne = px.line(dfOne, x='timeofdata', y=whichData, color='mac_address',
                     title="Battery Test", markers=True)
    
    # Convert the figure to JSON
    graphOneJson = json.dumps(figOne, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify(message='Battery data plotted successfully', graph=graphOneJson)

@app.route('/')
def index():
    

    # Pass the JSON to the template
    return render_template('index.html')

# API endpoint for Button 1
@app.route('/button1', methods=['POST'])
def button1():
    graphTwoJson = actionOne()
    return graphTwoJson

# API endpoint for Button 2
@app.route('/button2', methods=['POST'])
def button2():
    result = actionTwo()
    return jsonify({"message": result})

# API endpoint for Button 3
@app.route('/button3', methods=['POST'])
def button3():
    result = actionThree()
    return jsonify({"message": result})

# API endpoint for Button 4
@app.route('/button4', methods=['POST'])
def button4():
    result = actionFour()
    return jsonify({"message":                     result})

# API endpoint for Button 5
@app.route('/button5', methods=['POST'])
def button5():
    result = actionFive()
    return jsonify({"message": result})






if __name__ == '___main___':
    
    app.run(threaded=True, use_reloader=False)