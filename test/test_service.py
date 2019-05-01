import unittest
import mock

import os
import sys
import json
import yaml
import StringIO

sys.modules["RPi"] = mock.MagicMock()
sys.modules["RPi.GPIO"] = mock.MagicMock()

import RPi.GPIO
import service

class MockRedis(object):

    def __init__(self, host, port):

        self.host = host
        self.port = port
        self.channel = None
        self.messages = []

    def publish(self, channel, message):

        self.channel = channel
        self.messages.append(message)


class TestService(unittest.TestCase):

    @mock.patch.dict(os.environ, {
        "K8S_NODE": "pushy",
        "REDIS_CHANNEL": "stuff",
        "GPIO_PORT": "6",
        "SLEEP": "0.7"
    })
    @mock.patch("redis.StrictRedis", MockRedis)
    def setUp(self):

        self.daemon = service.Daemon()

    @mock.patch.dict(os.environ, {
        "K8S_NODE": "pushy",
        "REDIS_CHANNEL": "stuff",
        "GPIO_PORT": "6",
        "SLEEP": "0.7"
    })
    @mock.patch("redis.StrictRedis", MockRedis)
    def test___init___(self):

        daemon = service.Daemon()

        self.assertEqual(daemon.node, "pushy")
        self.assertEqual(daemon.redis.host, "host.docker.internal")
        self.assertEqual(daemon.redis.port, 6379)
        self.assertEqual(daemon.channel, "stuff")
        self.assertEqual(daemon.gpio_port, 6)
        self.assertEqual(daemon.sleep, 0.7)

    @mock.patch("RPi.GPIO.setmode")
    @mock.patch("RPi.GPIO.setup")
    def test_setup(self, mock_setup, mock_setmode):

        self.daemon.setup()

        mock_setmode.assert_called_once_with(RPi.GPIO.BCM)
        mock_setup.assert_called_once_with(6, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_DOWN)

    @mock.patch("RPi.GPIO.wait_for_edge")
    @mock.patch("RPi.GPIO.input")
    @mock.patch("service.time.time")
    @mock.patch("service.time.sleep")
    def test_process(self, mock_sleep, mock_time, mock_input, mock_wait):

        mock_time.return_value = 7
        mock_input.return_value = True

        self.daemon.process()

        mock_wait.assert_called_once_with(6, RPi.GPIO.RISING)
        mock_sleep.assert_called_once_with(0.7)
        mock_input.assert_called_once_with(6)

        self.assertEqual(self.daemon.redis.channel, "stuff")
        self.assertEqual(json.loads(self.daemon.redis.messages[0]), {
            "node": "pushy",
            "timestamp": 7,
            "type": "rising",
            "gpio_port": 6
        })

    @mock.patch("RPi.GPIO.setmode")
    @mock.patch("RPi.GPIO.setup")
    @mock.patch("RPi.GPIO.wait_for_edge")
    @mock.patch("RPi.GPIO.input")
    @mock.patch("service.time.time")
    @mock.patch("service.time.sleep")
    @mock.patch("traceback.format_exc")
    @mock.patch('sys.stdout', new_callable=StringIO.StringIO)
    def test_run(self, mock_print, mock_traceback, mock_sleep, mock_time, mock_input, mock_wait, mock_setup, mock_setmode):

        mock_time.return_value = 7
        mock_input.return_value = True

        mock_sleep.side_effect = [None, Exception("whoops"), Exception("whoops")]
        mock_traceback.side_effect = ["spirograph", Exception("doh")]

        self.assertRaisesRegexp(Exception, "doh", self.daemon.run)

        mock_setmode.assert_called_once_with(RPi.GPIO.BCM)
        mock_setup.assert_called_once_with(6, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_DOWN)

        mock_wait.assert_called_with(6, RPi.GPIO.RISING)
        mock_sleep.assert_called_with(0.7)
        mock_input.assert_called_with(6)

        self.assertEqual(self.daemon.redis.channel, "stuff")
        self.assertEqual(json.loads(self.daemon.redis.messages[0]), {
            "node": "pushy",
            "timestamp": 7,
            "type": "rising",
            "gpio_port": 6
        })

        self.assertEqual(mock_print.getvalue().split("\n")[:-1], [
            "whoops",
            "spirograph",
            "whoops"
        ])
