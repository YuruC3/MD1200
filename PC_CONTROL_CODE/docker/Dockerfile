FROM alpine:latest

# https://docs.docker.com/reference/dockerfile/#environment-replacement
ENV MD1200BAUD=38400
ENV SERIALADAPTER=/dev/ttyUSB0
ENV EPPYSLEEPY=300

# VOLUME [""]

RUN apk update && \
    apk add python3 py3-pip

RUN mkdir /etc/MD1200FAN/
WORKDIR /etc/MD1200FAN/

COPY ./mainDocker.py /etc/MD1200FAN/
# COPY ./requirements.txt /etc/MD1200FAN/

RUN python3 -m venv venv && \
    venv/bin/python3 -m pip install --upgrade pip && \
    venv/bin/pip3 install PySerial
    # venv/bin/pip3 install -r requirements.txt 

# VOLUME ["/etc/MD1200FAN/"]

CMD ["venv/bin/python3", "mainDocker.py"]

# CMD ["/etc/MD1200FAN/venv/bin/python3", "/etc/MD1200FAN/mainDocker.py"]