import serial, time, os

# setting consts that can be customized

# baud rate. Prob not needed as 38400 is standard
MD1200BAUD = int(os.getenv("MD1200BAUD", 38400))
# used if you want to run it on multiple JBODs
SERIALADAPTER = os.getenv("SERIALADAPTER", "/dev/ttyUSB0")
# Factor that defines how aggressive the temperature curve is
TEMP_FACTOR = int(os.getenv("TEMP_FACTOR", 19))
# time between sending command to get temp and storing it. It's there to allow JBOD to answer
EPPYSLEEPY = float(os.getenv("EPPYSLEEPY", 0.25))

LOW_FAN_TRSHD = int(os.getenv("LOW_FAN_TRSHD", 21))
HIGH_FAN_TRSHD = int(os.getenv("HIGH_FAN_TRSHD", 40))

GETTMPCMND = os.getenv("GETTMPCMND",  "_temp_rd")
SETFANCMND = os.getenv("SETFANCMND", "set_speed")

DEFOUTPRCNTG = int(os.getenv("DEFOUTPRCNTG", 24))



# init
MDserial = serial.Serial(
    port=SERIALADAPTER,\
    baudrate=MD1200BAUD,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=1)



def getTemp(inpMDreturning):
    MDict = {}

    # Sanitise output
    MDsanit = inpMDreturning.splitlines()

    #if there is smth do smth
    if inpMDreturning:

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
                case "AVG":
                    MDict["avg"] = int(line[12:14])
                case _:
                    continue
        return MDict


def setSpeed(inSpeeDict: dict):

    bpavrg = 0
    # default
    outfanprcntg = 0

    # get backplanbe average 
    if inSpeeDict["bp1"] and inSpeeDict["bp2"]:
        bpavrg = (inSpeeDict["bp1"] + inSpeeDict["bp2"]) /2
        outfanprcntg = int((bpavrg / (HIGH_FAN_TRSHD - LOW_FAN_TRSHD)) * TEMP_FACTOR)
        os.system(f"echo setting {outfanprcntg}%")

    # Set fan speed
    if outfanprcntg >= 20:
        MDserial.write((f"{SETFANCMND} {str(outfanprcntg)} \n\r").encode())  
        print(f"setting {outfanprcntg}%")
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

while True:
    # https://stackoverflow.com/questions/52578122/not-able-to-send-the-enter-command-on-pyserial

    # get temperature data, wait for MD1200 to answer and store 
    MDserial.write(f"{GETTMPCMND}\n\r".encode())
    time.sleep(EPPYSLEEPY)
    MDreturning = MDserial.read_until(" >").decode()

    MDtempDict = getTemp(MDreturning)
    setSpeedrcode = setSpeed(MDtempDict)

    # good
    if setSpeedrcode == 0:
        continue
        # print("Were mint")
        # time.sleep(EPPYSLEEPY)
    # not good
    elif setSpeedrcode == 1:
        print("Ambigous temperature readings.\nFalling back to safe values.")
        # time.sleep(EPPYSLEEPY)
    # very not good
    elif setSpeedrcode == -1:
        print("o nyo")
        exit()
    # very very very not good
    else:
        print("idk")
        exit()


print("closing port")
MDserial.close()
