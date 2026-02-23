import os
import logging
import threading
import psycopg2
import datetime
import time
from flask import Flask, jsonify
from miflora.miflora_poller import MiFloraPoller
from btlewrap.gatttool import GatttoolBackend as mifloragatt
from pygatt.backends import GATTToolBackend

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)

# Lock to prevent the polling loop and a manual scan from using the
# Bluetooth adapter at the same time, which would cause both to fail.
ble_lock = threading.Lock()

api = Flask(__name__)

@api.route('/scan', methods=['POST'])
def scan():
    log.info("BLE scan requested via API")
    macs = getsensormac()
    log.info(f"BLE scan complete, found: {macs}")
    return jsonify(macs=macs)

#read credentials from environment variables so they are not hardcoded in source
DB_HOST = os.environ.get('DB_HOST', '192.168.178.60')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'test_sensor')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASS = os.environ.get('DB_PASS', 'database')
BLE_ADAPTER = os.environ.get('BLE_ADAPTER', 'hci0')






def getsensormac():
    with ble_lock:
        adapter = GATTToolBackend(hci_device=BLE_ADAPTER)
        adapter.start()
        try:
            #scan for BLE devices - 15s gives sensors enough time to advertise
            devices = adapter.scan(timeout=15)
        finally:
            adapter.stop()

        macaddressReturn = []
        for device in devices:
            try:
                #only add macs of flower sensors
                if "Flower care" in device['name']:
                    log.info(f"Device found: {device['address']} ({device['name']})")
                    macaddressReturn.append(device['address'])
            except Exception as e:
                log.error(f"Could not process device {device}: {e}")
        return macaddressReturn


def loadsensormac():
    try:
        sensors = []
        sensorsUnformatted = open("macaddress.txt").readlines()
        for item in sensorsUnformatted:
            sensors.append(item.strip())
        return sensors
    except Exception as e:
        log.error(f"Could not load macs from macaddress.txt: {e}")
        return []

def getsensordata(sensors: list):
    data = {}
    if not sensors:
        raise Exception("Missing Macs, fetch Macs or add macaddress.txt")

    with ble_lock:
        for sensormac in sensors:
            try:
                log.info(f"Polling sensor with mac: {sensormac}")
                #polling for sensordata with btlewrap backend
                poller = MiFloraPoller(sensormac, mifloragatt, adapter=BLE_ADAPTER)
                temp = poller.parameter_value('temperature')
                light = poller.parameter_value('light')
                moisture = poller.parameter_value('moisture')
                conductivity = poller.parameter_value('conductivity')
                battery = poller.parameter_value('battery')
                #only add to data if polling succeeded - if above raises, this line is skipped
                data.update({sensormac:[temp,light,moisture,conductivity,battery]})
            except Exception as e:
                log.error(f"Failed to poll sensor {sensormac}, skipping database write: {e}")

    return data

def databasewrite(data: dict,table :str):
    
    try:
        #postgres connection
        conn=psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
            )
        #automaticly commit the SQL querys
        conn.autocommit = True
        cur = conn.cursor()

        #query to be filled with sensor data - use %s placeholders for safe parameterized queries
        query_sensor_data = f'INSERT INTO {table} VALUES(uuid_generate_v4(),now(),%s,%s,%s,%s,%s,%s);'

        #execute SQL querys for each sensor
        for mac, parameters in data.items():
            log.info(f"Inserting parameters into sensor_data for {mac}")
            cur.execute(query_sensor_data, (parameters[0],parameters[1],parameters[2],parameters[3],parameters[4],mac))

        #close connections 
        cur.close()
        conn.close()
        current_time = str(datetime.datetime.now())
        result = current_time + "  Successfully inserted data into database"
        return result
    except Exception as e:
        log.error(f"Could not connect to postgres server. Please check if the server is up and running! Error: {e}")


def ongoingPolling(period: int):
    while True:
        try:
            sensors = loadsensormac()
            data = getsensordata(sensors)
            result = databasewrite(data,"sensor_data")
            log.info(result)
        except Exception as e:
            log.error(f"Polling cycle failed, will retry in {period}s: {e}")
        time.sleep(period)

def pollingStart():

    log.info("Starting ongoing polling!!!")
    ongoingPolling(7200)


###MAIN

if __name__ == '__main__':
    api_thread = threading.Thread(
        target=lambda: api.run(host='0.0.0.0', port=8001, use_reloader=False),
        daemon=True
    )
    api_thread.start()
    pollingStart()
    





        