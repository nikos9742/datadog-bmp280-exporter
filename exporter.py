#!/usr/bin/env python3
from datadog import initialize, api
import time
from bmp280 import BMP280

options = {
    'api_key': ''
    ## EU costumers need to define 'api_host' as below
    #'api_host': 'https://api.datadoghq.eu/'
}

initialize(**options)

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

print("""Datadog Exporter for temperature and pressure.

Press Ctrl+C to exit!

""")

# Initialise the BMP280
bus = SMBus(1)
bmp280 = BMP280(i2c_dev=bus)

while True:
    now = time.time()
    future_10s = now + 10
    temperature = bmp280.get_temperature()
    pressure = bmp280.get_pressure()
    api.Metric.send(metric='bureau.temperature', points=temperature)
    api.Metric.send(metric='bureau.pressure', points=pressure)
    print('{:05.2f}*C {:05.2f}hPa'.format(temperature, pressure))
    print("Metrics sent !")
    time.sleep(30)
