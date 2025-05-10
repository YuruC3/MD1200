import serial, time

# CONST
MD1200BAUD = 38400
SERIALADAPTER = "/dev/ttyUSB0"  # In Windows it would be something like COM3

# init
MDserial = serial.Serial(
    port=SERIALADAPTER,\
    baudrate=MD1200BAUD,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS,\
    timeout=1)


# Check if UART is used
# Not neede because when defining MDserial it gets automatically opened
# try:
#     MDserial.open()
# except serial.serialutil.SerialException:
#     # MDserial.close()
#     # MDserial.open()
#     print("Port allready opened.\nTry closing it first")


def getTemp():
    print()

def setSpeed():
    print()

while True:
    MDreturning = MDserial.read_until(" >").decode()

    # sleep(50)
    MDfanspeed = getTemp(MDreturning)

    setSpeedrcode = setSpeed()

    if setSpeedrcode == 0:
        continue
    elif setSpeedrcode == -1:
        continue
    else:
        print("o nyo")
        exit()



    

# https://stackoverflow.com/questions/52578122/not-able-to-send-the-enter-command-on-pyserial
# MDserial.write("_temp_rd\n\r".encode())

# getTemp()
# print(MDserial.read_until(" >"))

# fanprct = 23

# MDserial.write(f"set_speed {fanprct}\n\r".encode())




# print("closing port")
# MDserial.close()
