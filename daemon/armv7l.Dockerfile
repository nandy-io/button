FROM klotio/rpi-raspbian:0.1

RUN apt-get update && \
    apt-get install -y python-pip python-dev python-rpi.gpio rpi-update && \
    SKIP_WARNING=1 rpi-update && \
    mkdir -p /opt/service

WORKDIR /opt/service

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD bin bin
ADD lib lib
ADD test test

ENV PYTHONPATH "/opt/service/lib:${PYTHONPATH}"

CMD "/opt/service/bin/daemon.py"
