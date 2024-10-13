import psycopg2 
import miflora
import pygatt
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

    with open("macadress.txt", "w") as macaddress:
        #only add macs of flower sensors
        for device in devices:
            if "Flower care" in str({device['name']}):
                print(f"Device found: {device['address']} ({device['name']})")
  
                macaddress.write(str({device['address']}) + "\n")
        #return list of found macs


def loadsensormac():
    sensors = []
    sensorsUnformatted = open("macadress.txt").readlines()
    for item in sensorsUnformatted:
        sensors.append(eval(item.strip()))
    return sensors

def getsensordata(sensors: list):
    data = {}
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

    
    return data

def databasewrite(data: dict):
    

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
        cur.execute(query_sensor_data.format("sensor_data",parameters[0],parameters[1],parameters[2],parameters[3],parameters[4],mac))

    #close connections 
    cur.close()
    conn.close()



####MAIN



def action_one():
    getsensormac()
    print('Fetched sensor macs')
def action_two():
    sensors = loadsensormac()
    data = getsensordata(sensors)

    databasewrite(data)
    print("Finished!")

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run()