import serial, time, os

# setting consts that can be customized

# baud rate. Prob not needed as 38400 is standard
MD1200BAUD = int(os.getenv("MD1200BAUD", 38400))
# used if you want to run it on multiple JBODs
SERIALADAPTER = os.getenv("SERIALADAPTER", "/dev/ttyUSB0")
# Factor that defines how aggressive the temperature curve is
TEMP_FACTOR = int(os.getenv("TEMP_FACTOR", 16))
# time between sending command to get temp and storing it. It's there to allow JBOD to answer
EPPYSLEEPY = float(os.getenv("EPPYSLEEPY", 1))

LOW_FAN_TRSHD = int(os.getenv("LOW_FAN_TRSHD", 21))
HIGH_FAN_TRSHD = int(os.getenv("HIGH_FAN_TRSHD", 40))

GETTMPCMND = os.getenv("GETTMPCMND",  "_temp_rd")
SETFANCMND = os.getenv("SETFANCMND", "set_speed")

DEFOUTPRCNTG = int(os.getenv("DEFOUTPRCNTG", 24))

MDSERIALTIMEOUT = float(os.getenv("MDSERIALTIMEOUT", 1))

TEMPREADINTERVAL = int(os.getenv("TEMPREADINTERVAL", 15))

GETTEMPTIMESLEEP = int(os.getenv("GETTEMPTIMESLEEP", 1))

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


def getTemp():

    MDserial.write(f"{GETTMPCMND}\n\r".encode())
    time.sleep(GETTEMPTIMESLEEP)
    MDreturning = MDserial.read_until(" >").decode(errors="ignore")

    MDict = {}

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
                            print(f"Could not parse AVG line: {line} ({e})", flush=True)
                            continue                    
                    # continue
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

# Init
MDtempDict = getTemp()
lastTempReading = time.time()
try:

    while True:
        # https://stackoverflow.com/questions/52578122/not-able-to-send-the-enter-command-on-pyserial

        # get temperature data, wait for MD1200 to answer and store 

        currentTime = time.time()

        if currentTime - lastTempReading >= TEMPREADINTERVAL:
            MDtempDict = getTemp()
            lastTempReading = currentTime
        
        if MDtempDict:
            setSpeedrcode = setSpeed(MDtempDict)

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

except KeyboardInterrupt:
    print("\n[INFO] KeyboardInterrupt detected. Exiting gracefully...")
    MDserial.close()
    exit()

finally:
    print("closing port")
    MDserial.close()

print("closing port")
MDserial.close()
