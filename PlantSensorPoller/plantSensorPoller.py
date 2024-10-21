import psycopg2 
import datetime
import time
from miflora.miflora_poller import MiFloraPoller
from btlewrap.gatttool import GatttoolBackend as mifloragatt
from pygatt.backends import GATTToolBackend






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
    ongoingPolling(7200)


###MAIN

if __name__ == '__main__':
    #starting thread for continously polling before the flask app
    pollingStart()
    print("Starting polling thread")





        