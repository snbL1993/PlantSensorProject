import psycopg2 
import miflora
from miflora.miflora_poller import MiFloraPoller
from btlewrap.gatttool import GatttoolBackend as mifloragatt
from pygatt.backends import GATTToolBackend
import pygatt

def getsensormac():
    adapter = GATTToolBackend()

    adapter.start()
    #scan for BLE devices
    devices = adapter.scan(timeout=5)
    sensors = []

    #only add macs of flower sensors
    for device in devices:
        if "Flower care" in str({device['name']}):
            print(f"Device found: {device['address']} ({device['name']})")
            sensors.append({device['address']})
    
    return sensors

def getsensordata(sensors: list):
    data = {}
    for sensormac in sensors:
        sensormac = str(sensormac).replace('{','')
        sensormac = sensormac.replace('}','')
        
        poller = MiFloraPoller(sensormac, mifloragatt)
        temp = poller.parameter_value('temperature')
        light = poller.parameter_value('light')
        moisture = poller.parameter_value('moisture')
        conductivity = poller.parameter_value('conductivity')
        battery = poller.parameter_value('battery')
        data.update({sensormac:[temp,light,moisture,conductivity,battery]})

    return data

def databasewrite(data: dir):
    print(data)

    conn=psycopg2.connect(
        host="192.168.178.60",
        port= 5432,database="test_sensor",
        user="postgres",
        password="database"
        )
    conn.autocommit = True

    cur = conn.cursor()
    query_sensor_data = 'INSERT INTO {} VALUES(uuid_generate_v4(),now(),{},{},{},{},{},{});'

    for mac, parameters in data:
        cur.execute(query_sensor_data.format("sensor_data",parameters[0],parameters[1],parameters[2],parameters[3],parameters[4],mac))

    cur.close()
    conn.close()



####MAIN


sensors = getsensormac()

data = getsensordata(sensors)

databasewrite(data)
