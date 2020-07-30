"""
Main module for daemon
"""

import os
import time

import json
import yaml
import redis
import RPi.GPIO

class Daemon(object):
    """
    Main class for daemon
    """

    def __init__(self):

        self.node = os.environ['NODE_NAME']
        self.hold = float(os.environ['HOLD'])
        self.sleep = float(os.environ['SLEEP'])

        self.redis = redis.StrictRedis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']))
        self.channel = os.environ['REDIS_CHANNEL']

        self.gpio_port = int(os.environ['GPIO_PORT'])

    def setup(self):
        """
        Sets up the GPIO modes and pins and pubsub
        """

        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setup(self.gpio_port, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_DOWN)

    def push(self):
        """
        Pushes the button
        """

        self.redis.publish(self.channel, json.dumps({
            "node": self.node,
            "timestamp": time.time(),
            "type": "rising",
            "gpio_port": self.gpio_port
        }))

    def process(self):
        """
        Processes a button being pushed
        """

        RPi.GPIO.wait_for_edge(self.gpio_port, RPi.GPIO.RISING)

        time.sleep(self.hold)

        if RPi.GPIO.input(self.gpio_port):
            self.push()

    def run(self):
        """
        Runs the daemon
        """

        self.setup()

        while True:
            self.process()
            time.sleep(self.sleep)
