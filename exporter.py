#!/usr/bin/env python3
import time
import yaml
import logging
from datadog import initialize, api
from bmp280 import BMP280
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

def launch_words():
    print("""Datadog Exporter for temperature and pressure.

    Press Ctrl+C to exit!

    """)

def smbus_init():
    # Initialise the BMP280
    bus = SMBus(1)
    bmp280 = BMP280(i2c_dev=bus)
    return bmp280

def open_configuration():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile)
    return cfg

def datadog_init():
    options = {
        'api_key': 'cfg["datadogkey"]'
        ## EU costumers need to define 'api_host' as below
        #'api_host': 'https://api.datadoghq.eu/'
    }
    initialize(**options)

def get_metrics_bmp280():
    temperature = bmp280.get_temperature()
    pressure = bmp280.get_pressure()
    return temperature, pressure

def send_metrics(result):
    metric_name1 = cfg[sensor_metric_name] + "temperature"
    metric_name2 = cfg[sensor_metric_name] + "pressure"
    api.Metric.send(metric=metric_name1, points=result[0])
    api.Metric.send(metric=metric_name2, points=result[1])
    if cfg["log_values"] : print("Metrics sent !")

def log_values_in_stdout(result):
    if cfg["log_values"] : print('{:05.2f}*C {:05.2f}hPa'.format(result[0], result[1]))

def sampling_interval_wait():
    time.sleep(int(cfg["sampling_interval"]))

def send_event(event):
    title = event["title"]
    text = event["text"]
    tags = ["cfg[sensor_metric_name]", "application:python-iot"]
    api.Event.create(title=title, text=text, tags=tags)
    print("Event sent !")


if __name__ == "__main__":
    while True:
        launch_words()
        bmp280 = smbus_init()
        cfg = open_configuration()
        datadog_init()
        event = {"title": "Launch script", "text": "The script has been launched"}
        send_event(event)
        event_error = ""
        while True:
            result = get_metrics_bmp280()
            log_values_in_stdout(result)
            try:
                if event_error != "":
                    send_event(event_error)
                    del event_error
                send_metrics(result)
            except Exception as e:
                event_error = {"title": "Error while sending metrics", "text": e}
                print(event_error)
            sampling_interval_wait()

