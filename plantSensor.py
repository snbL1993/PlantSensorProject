import psycopg2 
import miflora
from miflora.miflora_poller import MiFloraPoller
from pygatt.backends import GattToolBackend
import pygatt

def getsensormac():
    adapter = GattToolBackend()

    adapter.start()

    devices = adapter.scan(timeout=15)
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
        poller = MiFloraPoller(sensormac, GattToolBackend)
        data.update({sensormac:["this","is","a","test",1234]})

sensors = getsensormac()

getsensordata(sensors)