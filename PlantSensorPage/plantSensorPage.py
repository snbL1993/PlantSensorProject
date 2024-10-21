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


def action_one():
    result = "Currently not working!"
    return result

def action_two():

    result = "Currently not working!"
    return result

def action_three():

    result = "Currently not working!"
    return result

def action_four():

    result = "Currently not working!"
    return result

def action_five():

    result = "Currently not working!"
    return result

@app.route('/')
def index():
    whichData = 'moisture'
    dfOne = databaseread("sensor_data")
    dfOne['mac_address'] = dfOne['mac_address'].replace({'5c:85:7e:12:e2:b3' : 'Bogenhanf', '5c:85:7e:12:e3:d3' : 'Rosablätter'})
    # Create a Plotly figure
    figOne = px.line(dfOne, x='timeofdata', y=whichData, color='mac_address',
                     title="Moisture Test", markers=True)
    
    # Convert the figure to JSON
    graphOneJson = json.dumps(figOne, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Pass the JSON to the template
    return render_template('index.html', graph_one_json=graphOneJson)

# API endpoint for Button 1
@app.route('/button1', methods=['POST'])
def button1():
    result = action_one()
    return jsonify({"message": result})

# API endpoint for Button 2
@app.route('/button2', methods=['POST'])
def button2():
    result = action_two()
    return jsonify({"message": result})

# API endpoint for Button 3
@app.route('/button3', methods=['POST'])
def button2():
    result = action_three()
    return jsonify({"message": result})

# API endpoint for Button 4
@app.route('/button4', methods=['POST'])
def button2():
    result = action_four()
    return jsonify({"message": 
                    result})

# API endpoint for Button 5
@app.route('/button5', methods=['POST'])
def button2():
    result = action_five()
    return jsonify({"message": result})

if __name__ == '___main___':
    
    app.run(threaded=True, use_reloader=False)