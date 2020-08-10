import unittest
import unittest.mock
import klotio_unittest

import os
import sys
import json
import yaml

sys.modules["RPi"] = unittest.mock.MagicMock()
sys.modules["RPi.GPIO"] = unittest.mock.MagicMock()

import RPi.GPIO
import service

class TestService(klotio_unittest.TestCase):

    @unittest.mock.patch.dict(os.environ, {
        "NODE_NAME": "pushy",
        "REDIS_HOST": "most.com",
        "REDIS_PORT": "667",
        "REDIS_CHANNEL": "stuff",
        "GPIO_PORT": "6",
        "HOLD": "0.7",
        "SLEEP": "7.0"
    })
    @unittest.mock.patch("redis.Redis", klotio_unittest.MockRedis)
    @unittest.mock.patch("klotio_logger.setup", klotio_unittest.MockLogger)
    def setUp(self):

        self.daemon = service.Daemon()

    @unittest.mock.patch.dict(os.environ, {
        "NODE_NAME": "pushy",
        "REDIS_HOST": "most.com",
        "REDIS_PORT": "667",
        "REDIS_CHANNEL": "stuff",
        "GPIO_PORT": "6",
        "HOLD": "0.7",
        "SLEEP": "7.0"
    })
    @unittest.mock.patch("redis.Redis", klotio_unittest.MockRedis)
    @unittest.mock.patch("klotio_logger.setup", klotio_unittest.MockLogger)
    def test___init___(self):

        daemon = service.Daemon()

        self.assertEqual(daemon.node, "pushy")
        self.assertEqual(daemon.redis.host, "most.com")
        self.assertEqual(daemon.redis.port, 667)
        self.assertEqual(daemon.channel, "stuff")
        self.assertEqual(daemon.gpio_port, 6)
        self.assertEqual(daemon.hold, 0.7)
        self.assertEqual(daemon.sleep, 7.0)

        self.assertLogged(daemon.logger, "debug", "settings", extra={
            "settings": {
                "node": "pushy",
                "hold": 0.7,
                "sleep": 7.0,
                "redis": "MockRedis<host=most.com,port=667>",
                "channel": "stuff",
                "gpio_port": 6
            }
        })

    @unittest.mock.patch("RPi.GPIO.setmode")
    @unittest.mock.patch("RPi.GPIO.setup")
    def test_setup(self, mock_setup, mock_setmode):

        self.daemon.setup()

        mock_setmode.assert_called_once_with(RPi.GPIO.BCM)
        mock_setup.assert_called_once_with(6, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_DOWN)

        self.assertLogged(self.daemon.logger, "info", "setting up")

    @unittest.mock.patch("service.time.time")
    def test_press(self, mock_time):

        mock_time.return_value = 7

        self.daemon.press()

        self.assertEqual(self.daemon.redis.channel, "stuff")
        self.assertEqual(json.loads(self.daemon.redis.messages[0]), {
            "node": "pushy",
            "timestamp": 7,
            "type": "rising",
            "gpio_port": 6
        })

        self.assertLogged(self.daemon.logger, "info", "press", extra={
            "channel": "stuff",
            "press": {
                "node": "pushy",
                "timestamp": 7,
                "type": "rising",
                "gpio_port": 6
            }
        })

    @unittest.mock.patch("RPi.GPIO.wait_for_edge")
    @unittest.mock.patch("RPi.GPIO.input")
    @unittest.mock.patch("service.time.time")
    @unittest.mock.patch("service.time.sleep")
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

        self.assertLogged(self.daemon.logger, "debug", "waiting")
        self.assertLogged(self.daemon.logger, "debug", "rising")

    @unittest.mock.patch("RPi.GPIO.setmode")
    @unittest.mock.patch("RPi.GPIO.setup")
    @unittest.mock.patch("RPi.GPIO.wait_for_edge")
    @unittest.mock.patch("RPi.GPIO.input")
    @unittest.mock.patch("service.time.time")
    @unittest.mock.patch("service.time.sleep")
    def test_run(self, mock_sleep, mock_time, mock_input, mock_wait, mock_setup, mock_setmode):

        mock_time.return_value = 7
        mock_input.return_value = True

        mock_sleep.side_effect = [None, Exception("whoops")]

        self.assertRaisesRegex(Exception, "whoops", self.daemon.run)

        mock_setmode.assert_called_once_with(RPi.GPIO.BCM)
        mock_setup.assert_called_once_with(6, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_DOWN)

        mock_wait.assert_called_with(6, RPi.GPIO.RISING)
        mock_sleep.assert_called_with(7.0)
        mock_input.assert_called_with(6)

        self.assertEqual(self.daemon.redis.channel, "stuff")
        self.assertEqual(json.loads(self.daemon.redis.messages[0]), {
            "node": "pushy",
            "timestamp": 7,
            "type": "rising",
            "gpio_port": 6
        })
