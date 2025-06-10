#!/bin/bash
for i in {1..59}
do
    stty -F /dev/ttyUSB0 speed 38400 cs8 -ixon raw
    echo -ne "_shutup 24\n\r" > /dev/ttyUSB0
    sleep 1
done

exit
