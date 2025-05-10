import serial, time

# CONST
MD1200BAUD = 38400
SERIALADAPTER = "/dev/ttyUSB0"
GETTEMP = "_temp_rd"
SETFANPRCNT = "set_speed"
EPYSLEEPY = 300  # 5 minutes
#EPYSLEEPY = 150  # 2,5 minutes

# init
# MDserial = serial.Serial(
#     port=SERIALADAPTER,\
#     baudrate=MD1200BAUD,\
#     parity=serial.PARITY_NONE,\
#     stopbits=serial.STOPBITS_ONE,\
#     bytesize=serial.EIGHTBITS,\
#     timeout=1)

# After running .encode() on output
MDreturn = "b'\r\nBlueDress.105.001 >_temp_rd\r\n\r\n  BP_1[2] = 24c\r\n  BP_2[3] = 24c\r\n  SIM0[0] = 26c\r\n  SIM1[1] = 29c\r\n  EXP0[4] = 43c\r\n  EXP1[5] = 47c\r\n\r\n  AVG = 32c\r\n\r\nBlueDress.105.001 >'"
# before running .encode() on output
TrueMDeturn = MDreturn.encode()






def getTemp(inpMDreturning):
    # bp1 = 0
    # bp2 = 0
    # exp0 = 0
    # exp1 = 0
    # simm0 = 0
    # simm1 = 0
    # averr = 0
    MDict = {}

    # print("1")

    # Sanitise output
    MDsanit = inpMDreturning.splitlines()

    #if there is smth do smth
    if inpMDreturning:
        # print("2")

        # print(MDsanit)
        for line in MDsanit:
            # print(line)
            
            if ">" in line or "b'" in line:
                continue

            # print(line[2:])
            # if "BP_1" in line[2:]:
            #     print("yeeee")

            matchstm = line[2:6]

            # print(matchstm)

            match matchstm:
                case "BP_1":
                    # print("BP_1 " + line[12:14])
                    # bp1 = line[12:14]
                    MDict["bp1"] = int(line[12:14])
                case "BP_2":
                    # print("BP_2 " + line[12:14])
                    # bp2 = line[12:14]
                    MDict["bp2"] = int(line[12:14])
                case "SIM0":
                    # print("SIM0 " + line[12:14])
                    # simm0 = line[12:14]
                    MDict["sim0"] = int(line[12:14])
                case "SIM1":
                    # print("SIM1 " + line[12:14])
                    # simm1 = line[12:14]
                    MDict["sim1"] = int(line[12:14])
                case "EXP0":
                    # print("EXP0 " + line[12:14])
                    # exp0 = line[12:14]
                    MDict["exp0"] = int(line[12:14])
                case "EXP1":
                    # print("EXP1 " + line[12:14])
                    # exp1 = line[12:14]
                    MDict["exp1"] = int(line[12:14])
                case "AVG":
                    # print("AVG " + line[12:14])
                    # averr = line[12:14]
                    MDict["avg"] = int(line[12:14])
                case _:
                    print("ay men")
                    # continue

            # for thing in line.split(" ")[2:]:
            #     print(thing)
            # print(line[12:14])
        # print(MDsanit.split("\n"))

        return MDict
        # print(MDict)


# for key, thing in getTemp(MDreturn).items():
#     print(key, thing)

def setSpeed(inSpeeDict: dict):
    print("skibidi")

    bpavrg = 0
    # Some safe fan speedvalue
    defoutprntg = 27
    # default
    outfanprcntg = 0

    # Decide on fan speeds
    LOW_FAN_TRSHD = 21
    HIGH_FAN_TRSHD = 40
    TEMP_FACTOR = 21

    # DEBUG
    # for key, thing in inSpeeDict.items():
    #     print(key, thing)

    # get backplanbe average 
    if inSpeeDict["bp1"] and inSpeeDict["bp2"]:
        bpavrg = (inSpeeDict["bp1"] + inSpeeDict["bp2"]) /2


        outfanprcntg = int((bpavrg / (HIGH_FAN_TRSHD - LOW_FAN_TRSHD)) * TEMP_FACTOR)
        print(f"outfanprcntg is {outfanprcntg}")

    # Set fan speed
    if outfanprcntg >= 20:
        # MDserial.write(("set_speed " + str(outfanprcntg) + " \n\r").encode())  
        return 0
    else:
        # Set default value
        # MDserial.write(("set_speed " + str(defoutprntg) + " \n\r").encode())  
        return 1
    
    # If something goes super wrong
    return -1





while True:
# if True:
    # MDserial.write("_temp_rd\n\r".encode())

    # CHANGE AFTER TESTING 
    # MDreturning = MDserial.read_until(" >").decode()
    MDreturning = MDreturn

    # sleep(50)

    MDtempDict = getTemp(MDreturning)

    # setSpeed(MDtempDict)

    setSpeedrcode = setSpeed(MDtempDict)

    # good
    if setSpeedrcode == 0:
        print("Were mint")
        time.sleep(EPYSLEEPY)
    # not good
    elif setSpeedrcode == 1:
        print("Ambigous temperature readings.\nFalling back to safe values.")
        time.sleep(EPYSLEEPY)
    # very not good
    elif setSpeedrcode == -1:
        print("o nyo")
        exit()
    # very very very not good
    else:
        print("idk")









# def getTemp():
#     bp1 = 0
#     bp2 = 0
#     #exp0 = 0
#     #exp1 = 0
#     #simm0 = 0
#     #simm1 = 0
#     getMD1200tempReturn = ""

#     MDserial.write(GETTEMP.encode())
    
#     print(MDserial.readlines())

#     MDreturning = MDserial.readlines().decode()
#     #if there is smth do smth
#     if len(MDreturning) >= 1:
#         print("skibidi")
#         return MDreturning

# try:
#     MDserial.open()
# except serial.serialutil.SerialException:
#     print("Port allready opened.\nTry closing it first")
    

# # https://stackoverflow.com/questions/52578122/not-able-to-send-the-enter-command-on-pyserial
# MDserial.write("_temp_rd\n\r".encode())


# print(MDserial.read_until(" >"))

# fanprct = 23

# MDserial.write(f"set_speed {fanprct}\n\r".encode())

# MDserial.close()