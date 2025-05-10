# MD1200 fan noise reduction 

A set of scripts that automagically set fan speed on a MD1200 (probably MD1220 as well) based on internal temperature readings.

## PC

### Docker

In .env file change 

```serial_adapter``` which is a serial port you're using. 
On linux it is /dev/ttyUSBx and on windows it is COMx

```wait_time``` is the interval in which script is checking temperature. By default it is 300 seconds, which is 5 minutes.

### Systemd 

First create virtual enviroment

```
python3 -m venv venv
```

Then install required modules
```
venv/bin/pip3 install PySerial
```
After that you just need to change a few things
```SERIALADAPTER``` to a port you're using. 

On linux it is /dev/ttyUSBx and on windows it is COMx


```EPPYSLEEPY``` is the interval in which script is checking temperature. By default it is 300 seconds, which is 5 minutes.

### Proxmox LXC

You can also run it in LXC container on your Proxmox host. Just follow the [systemd](###systemd) instructions.

Here you will also need to add ```/dev/ttyUSBx``` to your LXC container. You do it under Resources -> Add -> Device Passthrough -> ```/dev/ttyUSBx``` as Device Path. 

## STM32F103C6T6

I think it needs a MAX2323 between MD1200.

Will look into that.

## Arduino Nano

Same here


### FAQ

dc: yuruc3