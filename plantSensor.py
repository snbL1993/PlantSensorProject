import psycopg2 
import miflora
from miflora.miflora_poller import MiFloraPoller
from pygatt.backends import GATTToolBackend
import pygatt

def getsensormac():
    adapter = GATTToolBackend()

    adapter.start()

    devices = adapter.scan(timeout=5)
    sensors = []

    for device in devices:
        if "Flower care" in str({device['name']}):
            print(f"Device found: {device['address']} ({device['name']})")
            sensors.append({device['address']})
    print(sensors)
    return sensors

def getsensordata(sensors: list):
    data = {}
    for sensormac in sensors:
        sensormac = str(sensormac).replace('{','')
        sensormac = sensormac.replace('}','')
        print(sensormac)
        poller = MiFloraPoller(sensormac, GATTToolBackend)
        data.update({sensormac:["this","is","a","test",1234]})

    print(data)


####MAIN


sensors = getsensormac()

getsensordata(sensors)