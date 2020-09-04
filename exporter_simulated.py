#!/usr/bin/env python3
import time
import yaml
import logging
import random
from datadog import initialize, api

def launch_words():
    print("""Datadog Exporter for custom metrics via API.

    Press Ctrl+C to exit!

    """)

def open_configuration():
    with open("config2.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
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

def send_metrics(result,cfg):
    metric_name1 = cfg["sensor_metric_name"] + "." + "temperature"
    metric_name2 = cfg["sensor_metric_name"] + "." + "pressure"
    a1 = api.Metric.send(metric=str(metric_name1), points=int(result[0]))
    a2 = api.Metric.send(metric=str(metric_name2), points=int(result[1]))
    if cfg["log_values"] : print("Metrics sent ! " + metric_name1 + " " + metric_name2)
    print(a1)
    print(a2)

def send_event(event,cfg):
    title = event["title"]
    text = event["text"]
    applicationtag = "application:" + cfg["application"]
    tags = [cfg["sensor_metric_name"], applicationtag]
    api.Event.create(title=title, text=text, tags=tags)
    print("Event sent !")

def sampling_interval_wait(cfg):
    time.sleep(int(cfg["sampling_interval"]))

def simulate_temp():
    TEMPERATURE = 20.0
    HUMIDITY = 60
    temperature = TEMPERATURE + (random.random() * 15)
    humidity = HUMIDITY + (random.random() * 20)
    return temperature, humidity


if __name__ == "__main__":
    while True:
        launch_words()
        cfg = open_configuration()
        options = {
            'api_key': 'cfg["datadogkey"]'
            ## EU costumers need to define 'api_host' as below
            #'api_host': 'https://api.datadoghq.eu/'
        }
        initialize(**options)
        print("Datadog Init ...")
        event = {"title": "Launch script", "text": "The script has been launched"}
        send_event(event,cfg)
        event_error = ""
        while True:
            result = simulate_temp()
            print(result)
            try:
                if event_error != "":
                    send_event(event_error,cfg)
                    del event_error
                send_metrics(result,cfg)
            except Exception as e:
                event_error = {"title": "Error while sending metrics", "text": e}
                print(event_error)
            sampling_interval_wait(cfg)