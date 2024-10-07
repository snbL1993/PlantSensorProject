import psycopg2 
from pygatt.backends import GATTToolBackend
import pygatt

def getsensormac():
    adapter = GATTToolBackend()

    adapter.start()

    devices = adapter.scan(timeout=15)
    sensors = []

    for device in devices:
        print(device['name'])
        if "Flower care" in str({device['name']}):
            print(f"Device found: {device['address']} ({device['name']})")
            sensors.append({device['address']})
    print(sensors)


getsensormac()