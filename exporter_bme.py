#!/usr/bin/env python3
import time
import yaml
import logging
from datadog import initialize, api
try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus
from bme280 import BME280

def launch_words():
    print("""Datadog Exporter for temperature and pressure.

    Press Ctrl+C to exit!

    """)

def smbus_init():
    # Initialise the BME280
    bus = SMBus(1)
    bme280 = BME280(i2c_dev=bus)
    print("smbus_init Init ...")
    return bme280

def open_configuration():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile)
        print("Configuration Init ...")
    return cfg

def datadog_init():
    options = {
        'api_key': cfg["datadogkey"]
        ## EU costumers need to define 'api_host' as below
        #'api_host': 'https://api.datadoghq.eu/'
    }
    initialize(**options)
    print("Datadog Init ...")

def get_metrics_bme280():
    temperature = bme280.get_temperature()
    pressure = bme280.get_pressure()
    humidity = bme280.get_humidity()
    return temperature, pressure, humidity

def send_metrics(result,cfg):
    metric_name1 = cfg["sensor_metric_name"] + "." + "temperature"
    metric_name2 = cfg["sensor_metric_name"] + "." + "pressure"
    metric_name3 = cfg["sensor_metric_name"] + "." + "humidity"
    api.Metric.send(metric=str(metric_name1), points=result[0])
    api.Metric.send(metric=str(metric_name2), points=result[1])
    api.Metric.send(metric=str(metric_name3), points=result[2])
    if cfg["log_values"] : print("Metrics sent ! " + metric_name1 + " " + metric_name2 + " " + metric_name3)

def log_values_in_stdout(result,cfg):
    if cfg["log_values"] : print('{:05.2f}*C {:05.2f}hPa {:05.2f}%'.format(temperature, pressure, humidity))

def sampling_interval_wait(cfg):
    time.sleep(int(cfg["sampling_interval"]))

def send_event(event,cfg):
    title = event["title"]
    text = event["text"]
    tags = [cfg["sensor_metric_name"], "application:python-iot"]
    api.Event.create(title=title, text=text, tags=tags)
    print("Event sent !")

if __name__ == "__main__":
    while True:
        launch_words()
        bme280 = smbus_init()
        cfg = open_configuration()
        datadog_init()
        event = {"title": "Launch script", "text": "The script has been launched"}
        send_event(event,cfg)
        event_error = ""
        while True:
            result = get_metrics_bme280()
            log_values_in_stdout(result,cfg)
            try:
                if event_error != "":
                    send_event(event_error,cfg)
                    del event_error
                send_metrics(result,cfg)
            except Exception as e:
                event_error = {"title": "Error while sending metrics", "text": e}
                print(event_error)
            sampling_interval_wait(cfg)

