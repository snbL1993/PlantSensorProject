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
    print(sensors)
    return sensors

def getsensordata(sensors: list):
    data = {}
    for sensormac in sensors:
        sensormac = str(sensormac).replace('{','')
        sensormac = sensormac.replace('}','')
        print(sensormac)
        poller = MiFloraPoller(sensormac, mifloragatt)
        temp = poller.parameter_value('temperature')
        light = poller.parameter_value('light')
        moisture = poller.parameter_value('moisture')
        conductivity = poller.parameter_value('conductivity')
        battery = poller.parameter_value('battery')
        data.update({sensormac:[temp,light,moisture,conductivity,battery]})

    print(data)


####MAIN


sensors = getsensormac()

getsensordata(sensors)