from pygatt.backends import GATTToolBackend
import pygatt

adapter = GATTToolBackend()

adapter.start()

sensors = adapter.scan(timeout=15)


for device in sensors:
    print(f"Device found: {device['address']} ({device['name']})")