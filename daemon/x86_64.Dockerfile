FROM debian:jessie

RUN apt-get update && \
    apt-get install -y python-pip && \
	mkdir -p /opt/nandy-io

WORKDIR /opt/nandy-io

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD bin bin
ADD lib lib
ADD test test

ENV PYTHONPATH "/opt/nandy-io/lib:${PYTHONPATH}"

CMD "/opt/nandy-io/bin/daemon.py"
