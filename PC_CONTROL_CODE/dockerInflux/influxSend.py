import time, os, influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS, WriteOptions
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor


# INFLUXDB config
# token = "apg1gysUeCcxdcRTMmosJTenbEppmUNi9rXlANDB2oNadBdWAu2GVTDc_q_dyo0iyYsckKaOvPRm6ba2NK0y_A=="
token = os.getenv("INFLUX_TOKEN")
# bucket = "JBOD"
bucket = os.getenv("INFLUX_BUCKET")
# org = "staging"
org = os.getenv("INFLUX_ORG")
# url = "http://localhost:8086"
url = os.getenv("INFLUX_URL")
# measurement = "MD1200"
measurement = os.getenv("INFLUX_MEASUREMENT")
# MACHINE_TAG = "CHONGUS1200"
MACHINE_TAG = os.getenv("INFLUX_MACHINE_TAG")
# LOCATION = "HQ"
LOCATION = os.getenv("INFLUX_LOCATION")
# INFLX_SEPARATE_POINTS = 0.1
INFLUX_SEPARATE_POINTS = int(os.getenv("INFLUX_SEPARATE_POINTS"))

# Initialize InfluxDB client and influxdb API
inflxdb_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
#write_api = inflxdb_client.write_api(write_options=SYNCHRONOUS)
write_api = inflxdb_client.write_api(write_options=WriteOptions(batch_size=500, flush_interval=1000))

# Threaded flow processor
def process_temps(inEntry):
    global MDict

    # ---LeData---
    # {'bp1': 35, 'bp2': 29, 'sim0': 35, 'sim1': 34, 'exp0': 56, 'exp1': 54}
    # ---LeData---

    # Prep InfluxDB data
    inflxdb_Data_To_Send = (
        influxdb_client.Point(f"{measurement}-script")
        .tag("MACHINE", MACHINE_TAG)
        .tag("LOCATION", LOCATION)
        .field("Backplane1", inEntry["bp1"])
        .field("Backplane2", inEntry["bp2"])
        .field("SASIntModule0", inEntry["sim0"])
        .field("SASIntModule1", inEntry["sim1"])
        .field("Expander0", inEntry["exp0"])
        .field("Expander1", inEntry["exp1"])
        .field("Average", inEntry["avg"])
    )

    print("----------------")
    return ()
