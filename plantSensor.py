import psycopg2 
import miflora
import pygatt
import datetime
import json
import plotly
import plotly.express as px
import pandas
import time
import sqlalchemy
import threading
from miflora.miflora_poller import MiFloraPoller
from btlewrap.gatttool import GatttoolBackend as mifloragatt
from pygatt.backends import GATTToolBackend
from flask import Flask, render_template, jsonify



app = Flask(__name__)

def getsensormac():
    adapter = GATTToolBackend()

    adapter.start()
    #scan for BLE devices
    devices = adapter.scan(timeout=5)
    macaddressReturn = []
    with open("macaddress.txt", "w") as macaddress:
        try:
            #only add macs of flower sensors
            for device in devices:
                if "Flower care" in str({device['name']}):
                    print(f"Device found: {device['address']} ({device['name']})")
    
                    macaddress.write(str({device['address']}) + "\n")
                    macaddressReturn.append(str({device['address']}))
        except:
            print("Could not write macs to file")        
    result = str(macaddressReturn)
    return result


def loadsensormac():
    try:
        sensors = []
        sensorsUnformatted = open("macaddress.txt").readlines()
        for item in sensorsUnformatted:
            sensors.append(eval(item.strip()))
        return sensors
    except:
        print("Could not load macs from macaddress.txt")

def getsensordata(sensors: list):
    data = {}
    if not sensors:
        raise Exception("Missing Macs, fetch Macs or add macaddress.txt")
    try:
        for sensormac in sensors:
            print(f"Polling sensor with mac: {sensormac} ")
            #rewrite mac to needed format
            sensormac = str(sensormac).replace('{','')
            sensormac = sensormac.replace('}','')

            #polling for sensordata with btlewrap backend
            poller = MiFloraPoller(sensormac, mifloragatt)
            temp = poller.parameter_value('temperature')
            light = poller.parameter_value('light')
            moisture = poller.parameter_value('moisture')
            conductivity = poller.parameter_value('conductivity')
            battery = poller.parameter_value('battery')

            #adding entry for each mac with polled parameters
            data.update({sensormac:[temp,light,moisture,conductivity,battery]})
    except:
        print("Failed to poll data or write do database")
    
    return data

def databasewrite(data: dict,table :str):
    

    #postgres connection
    conn=psycopg2.connect(
        host="192.168.178.60",
        port= 5432,
        database="test_sensor",
        user="postgres",
        password="database"
        )
    #automaticly commit the SQL querys
    conn.autocommit = True
    cur = conn.cursor()

    #query to be filled with sensor data
    query_sensor_data = 'INSERT INTO {} VALUES(uuid_generate_v4(),now(),{},{},{},{},{},{});'

    #execute SQL querys for each sensor
    for mac, parameters in data.items():
        print(f"Inserting parameters into sensor_data for {mac}")
        cur.execute(query_sensor_data.format(table,parameters[0],parameters[1],parameters[2],parameters[3],parameters[4],mac))

    #close connections 
    cur.close()
    conn.close()
    current_time = str(datetime.datetime.now())
    result = current_time + "  Successfully inserted data into database"
    return result

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


def ongoingPolling(period: int):
    while True:
        sensors = loadsensormac()
        data = getsensordata(sensors)
        result = databasewrite(data,"sensor_data")
        print(result)
        time.sleep(period)

def isFullHour():
    now = datetime.datetime.now()
    return now.minute == 0 and now.second == 0
    
def pollingStart():

    print("Starting ongoing polling!!!")
    ongoingPolling(1800)


####Flask



def action_one():
    result = getsensormac()
    print('Fetched sensor macs')
    return result

def action_two():
    sensors = loadsensormac()
    data = getsensordata(sensors)

    result = databasewrite(data,"sensor_data")
    print("Finished!")
    return result



@app.route('/')
def index():
   
    dfOne = databaseread("sensor_data")
    dfOne['mac_address'] = dfOne['mac_address'].replace({'5c:85:7e:12:e2:b3' : 'Bogenhanf', '5c:85:7e:12:e3:d3' : 'Rosablätter'})
    # Create a Plotly figure
    figOne = px.line(dfOne, x='timeofdata', y='moisture', color='mac_address',
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


###MAIN

if __name__ == '__main__':
    #starting thread for continously polling before the flask app
    polling_thread = threading.Thread(target=pollingStart)
    polling_thread.daemon = True  # So that it exits when the main program exits
    polling_thread.start()
    
    app.run()


        