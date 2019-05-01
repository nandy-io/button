"""
Main module for daemon
"""

import os
import time
import traceback

import json
import yaml
import redis
import RPi.GPIO

class Daemon(object):
    """
    Main class for daemon
    """

    def __init__(self):

        self.node = os.environ['K8S_NODE']
        self.sleep = float(os.environ['SLEEP'])

        with open("/opt/nandy-io/subscriptions/redis.yaml", "r") as redis_file:
            redis_config = yaml.safe_load(redis_file)

        self.redis = redis.StrictRedis(host=redis_config["host"], port=redis_config["port"])

        self.channel = os.environ['REDIS_CHANNEL']
        self.gpio_port = int(os.environ['GPIO_PORT'])

    def setup(self):
        """
        Sets up the GPIO modes and pins and pubsub
        """

        RPi.GPIO.setmode(RPi.GPIO.BCM)  
        RPi.GPIO.setup(self.gpio_port, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_DOWN)

    def process(self):
        """
        Processes a button being pushed
        """

        RPi.GPIO.wait_for_edge(self.gpio_port, RPi.GPIO.RISING)

        time.sleep(self.sleep)

        if RPi.GPIO.input(self.gpio_port):
            self.redis.publish(self.channel, json.dumps({
                "node": self.node,
                "timestamp": time.time(),
                "type": "rising",
                "gpio_port": self.gpio_port
            }))
            
    def run(self):
        """
        Runs the daemon
        """

        self.setup()

        while True:
            try:
                self.process()
            except Exception as exception:
                print(exception)
                print(traceback.format_exc())
