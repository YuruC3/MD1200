import serial, time, os

# CONST
if os.environ["MD1200BAUD"]:
    MD1200BAUD = int(os.environ["MD1200BAUD"])
else:
    MD1200BAUD = 38400

if os.environ["SERIALADAPTER"]:
    SERIALADAPTER = os.environ["SERIALADAPTER"]
else:
    SERIALADAPTER = "/dev/ttyUSB0"

GETTEMP = "_temp_rd"
SETFANPRCNT = "set_speed"

if os.environ["EPPYSLEEPY"]:
    EPPYSLEEPY = int(os.environ["EPPYSLEEPY"])
else:
    EPPYSLEEPY = 1  # 1 second

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
    # Some safe fan speedvalue
    defoutprntg = 27
    # default
    outfanprcntg = 0

    # Decide on fan speeds
    LOW_FAN_TRSHD = 21
    HIGH_FAN_TRSHD = 40
    TEMP_FACTOR = 19

    # get backplanbe average 
    if inSpeeDict["bp1"] and inSpeeDict["bp2"]:
        bpavrg = (inSpeeDict["bp1"] + inSpeeDict["bp2"]) /2

        outfanprcntg = int((bpavrg / (HIGH_FAN_TRSHD - LOW_FAN_TRSHD)) * TEMP_FACTOR)

    # Set fan speed
    if outfanprcntg >= 20:
        MDserial.write(("set_speed " + str(outfanprcntg) + " \n\r").encode())  
        print(f"setting {outfanprcntg}%")
        return 0
    else:
        # Set default value
        MDserial.write(("set_speed " + str(defoutprntg) + " \n\r").encode())  
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
    MDserial.write("_temp_rd\n\r".encode())
    time.sleep(1)
    MDreturning = MDserial.read_until(" >").decode()

    MDtempDict = getTemp(MDreturning)
    setSpeedrcode = setSpeed(MDtempDict)

    # good
    if setSpeedrcode == 0:
        # print("Were mint")
        time.sleep(EPPYSLEEPY)
    # not good
    elif setSpeedrcode == 1:
        print("Ambigous temperature readings.\nFalling back to safe values.")
        time.sleep(EPPYSLEEPY)
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
