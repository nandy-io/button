"""
Main module for daemon
"""

# pylint: disable=no-member

import os
import time

import json
import redis
import RPi.GPIO

import klotio

class Daemon:
    """
    Main class for daemon
    """

    def __init__(self):

        self.node = os.environ['NODE_NAME']
        self.hold = float(os.environ['HOLD'])
        self.sleep = float(os.environ['SLEEP'])

        self.redis = redis.Redis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']))
        self.channel = os.environ['REDIS_CHANNEL']

        self.gpio_port = int(os.environ['GPIO_PORT'])

        self.logger = klotio.logger("nandy-io-button-daemon")

        self.logger.debug("init", extra={
            "init": {
                "node": self.node,
                "hold": self.hold,
                "sleep": self.sleep,
                "redis": {
                    "connection": str(self.redis),
                    "channel": self.channel
                },
                "gpio_port": self.gpio_port
            }
        })

    def setup(self):
        """
        Sets up the GPIO modes and pins and pubsub
        """

        self.logger.info("setting up")

        RPi.GPIO.setmode(RPi.GPIO.BCM)
        RPi.GPIO.setup(self.gpio_port, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_DOWN)

    def press(self):
        """
        Pushes the button
        """

        press = {
            "node": self.node,
            "timestamp": time.time(),
            "type": "rising",
            "gpio_port": self.gpio_port
        }

        self.logger.info("press", extra={"channel": self.channel, "press": press})

        self.redis.publish(self.channel, json.dumps(press))

    def process(self):
        """
        Processes a button being pushed
        """

        self.logger.debug("waiting")

        RPi.GPIO.wait_for_edge(self.gpio_port, RPi.GPIO.RISING)

        self.logger.debug("rising")

        time.sleep(self.hold)

        if RPi.GPIO.input(self.gpio_port):
            self.press()

    def run(self):
        """
        Runs the daemon
        """

        self.setup()

        while True:
            self.process()
            time.sleep(self.sleep)
