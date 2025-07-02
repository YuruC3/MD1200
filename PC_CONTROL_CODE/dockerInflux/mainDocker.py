import time, os, influxdb_client, serial, threading
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS, WriteOptions
from concurrent.futures import ThreadPoolExecutor

# setting consts that can be customized

# baud rate. Prob not needed as 38400 is standard
MD1200BAUD = int(os.getenv("MD1200BAUD", 38400))
# used if you want to run it on multiple JBODs
SERIALADAPTER = os.getenv("SERIALADAPTER", "/dev/ttyUSB0")
# Factor that defines how aggressive the temperature curve is
TEMP_FACTOR = int(os.getenv("TEMP_FACTOR", 19))
# time between sending command to get temp and storing it. It's there to allow JBOD to answer
EPPYSLEEPY = float(os.getenv("EPPYSLEEPY", 1))

LOW_FAN_TRSHD = int(os.getenv("LOW_FAN_TRSHD", 21))
HIGH_FAN_TRSHD = int(os.getenv("HIGH_FAN_TRSHD", 40))

GETTMPCMND = os.getenv("GETTMPCMND",  "_temp_rd")
SETFANCMND = os.getenv("SETFANCMND", "set_speed")

DEFOUTPRCNTG = int(os.getenv("DEFOUTPRCNTG", 24))

MDSERIALTIMEOUT = float(os.getenv("MDSERIALTIMEOUT", 1))

TEMPREADINTERVAL = float(os.getenv("TEMPREADINTERVAL", 15))

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
# INFLUX_SEPARATE_POINTS = float(os.getenv("INFLUX_SEPARATE_POINTS"), 0.1)

# init
MDserial = serial.Serial(
    port=SERIALADAPTER,\
    baudrate=MD1200BAUD,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=MDSERIALTIMEOUT)

lastTempReading = time.time() 
MDtempDict = {}
MDict = {}
fluxSending = False
currentTime = 0
lastTempReading = 0
inflxdb_LeData = []
# Initialize InfluxDB client and influxdb API
# ---------------------UNCOMMENT-----------------------
inflxdb_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = inflxdb_client.write_api(write_options=SYNCHRONOUS)
# ---------------------UNCOMMENT-----------------------


def getTemp():
    global MDict, fluxSending

    MDserial.write(f"{GETTMPCMND}\n\r".encode())
    time.sleep(1)
    MDreturning = MDserial.read_until(" >").decode()

    # MDict = {}

    # Sanitise output
    MDsanit = MDreturning.splitlines()

    #if there is smth do smth
    if MDreturning:

        for line in MDsanit:
            
            if ">" in line or "b'" in line:
                continue

            matchstm = line[2:6]

            match matchstm:
                case "BP_1":
                    MDict["bp1"] = int(line[12:14])
                case "BP_2":
                    MDict["bp2"] = int(line[12:14])
                case "SIM0":
                    MDict["sim0"] = int(line[12:14])
                case "SIM1":
                    MDict["sim1"] = int(line[12:14])
                case "EXP0":
                    MDict["exp0"] = int(line[12:14])
                case "EXP1":
                    MDict["exp1"] = int(line[12:14])
                # case "AVG":
                    # MDict["avg"] = int(line[12:14])
                    # MDict["avg"] = int(line.strip().split("=")[1].strip().replace("c", ""))
                    # try:
                    #     # Extract number from e.g. '  AVG = 40c'
                    #     temp = int(line.strip().split("=")[1].strip().replace("c", ""))
                    #     MDict["avg"] = temp
                    # except Exception as e:
                    #     # print(f"[WARN] Failed to parse AVG line: {line} ({e})", flush=True)
                    #     pass
                case _:
                    # try to catch the AVG line like: "  AVG = 40c"
                    stripped = line.strip()
                    if stripped.startswith("AVG"):
                        try:
                            temp = int(stripped.split("=")[1].strip().replace("c", ""))
                            MDict["avg"] = temp
                        except Exception as e:
                            print(f"[WARN] Could not parse AVG line: {line} ({e})", flush=True)
                            continue                    
                    # continue
    
        
        # {'bp1': 35, 'bp2': 29, 'sim0': 35, 'sim1': 33, 'exp0': 56, 'exp1': 54, 'avg': 40}
        # process_temps(MDict)
        fluxSending = True

        return MDict


def setSpeed(inSpeeDict: dict):

    bpavrg = 0
    # default
    outfanprcntg = 0

    # get backplanbe average 
    if "bp1" in inSpeeDict and "bp2" in inSpeeDict:
        bpavrg = (inSpeeDict["bp1"] + inSpeeDict["bp2"]) /2
        outfanprcntg = int((bpavrg / (HIGH_FAN_TRSHD - LOW_FAN_TRSHD)) * TEMP_FACTOR)
        # os.system(f"echo setting {outfanprcntg}%")

    # Set fan speed
    if outfanprcntg >= 20:
        MDserial.write((f"{SETFANCMND} {str(outfanprcntg)} \n\r").encode())  
        print(f"setting {outfanprcntg}%", flush=True)
        return 0
    else:
        # Set default value
        MDserial.write((f"{SETFANCMND} {str(DEFOUTPRCNTG)} \n\r").encode())  
        return 1
    
    # If something goes super wrong
    return -1



# Check if UART is used
# Not neede because when defining MDserial it gets automatically opened
# Will leave it here anyway
# try:
#     MDserial.open()
# except serial.serialutil.SerialException:
#     # MDserial.close()
#     # MDserial.open()
#     print("Port allready opened.\nTry closing it first")

# Threaded flow processor
def process_temps():
    global MDict, fluxSending

    while True:
        # ---LeData---
        # {'bp1': 35, 'bp2': 29, 'sim0': 35, 'sim1': 34, 'exp0': 56, 'exp1': 54}
        # ---LeData---
        if fluxSending:
        # Prep InfluxDB data
            inflxdb_Data_To_Send = (
                influxdb_client.Point(f"{measurement}-script")
                .tag("MACHINE", MACHINE_TAG)
                .tag("LOCATION", LOCATION)
                .field("Backplane1", MDict["bp1"])
                .field("Backplane2", MDict["bp2"])
                .field("SASIntModule0", MDict["sim0"])
                .field("SASIntModule1", MDict["sim1"])
                .field("Expander0", MDict["exp0"])
                .field("Expander1", MDict["exp1"])
                .field("Average", MDict["avg"])
            )

            # Prep/append data
            inflxdb_LeData.append(inflxdb_Data_To_Send)
            # Send data to InfluxDB
            write_api.write(bucket=bucket, org=org, record=inflxdb_Data_To_Send)


            # Clean up before another loop
            inflxdb_LeData.clear()
            print("Sending data to InfluxDB", flush=True)

            fluxSending = False

        else:
            time.sleep(0.25)




# Init
MDict = getTemp()
lastTempReading = time.time()

def mainCodeHere():
    while True:
        global MDict, fluxSending, currentTime, lastTempReading
        # https://stackoverflow.com/questions/52578122/not-able-to-send-the-enter-command-on-pyserial

        # get temperature data, wait for MD1200 to answer and store 

        currentTime = time.time()

        if currentTime - lastTempReading >= TEMPREADINTERVAL:
            getTemp()
            lastTempReading = currentTime
        
        if MDict:
            setSpeedrcode = setSpeed(MDict)

            # good
            if setSpeedrcode == 0:
                pass
                # print("Were mint", flush=True)
                # time.sleep(EPPYSLEEPY)
            # not good
            elif setSpeedrcode == 1:
                print("Ambigous temperature readings.\nFalling back to safe values.", flush=True)
                # time.sleep(EPPYSLEEPY)
            # very not good
            elif setSpeedrcode == -1:
                print("o nyo", flush=True)
                exit()
            # very very very not good
            else:
                print("idk", flush=True)
                exit()
        else:
            print(f"temperature not yet pulled.\nFalling back do default fan speed", flush=True)
            # os.system(f"echo temperature not yet pulled.\nFalling back do default fan speed")
            MDserial.write((f"{SETFANCMND} {str(DEFOUTPRCNTG)} \n\r").encode()) 

        time.sleep(EPPYSLEEPY) 


# Prepare threads and launch them
thread_main = threading.Thread(target=mainCodeHere)
thread_flux = threading.Thread(target=process_temps)

thread_main.start()
thread_flux.start()

thread_main.join()
thread_flux.join()