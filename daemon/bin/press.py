#!/usr/bin/env python

import unittest.mock

import sys

sys.modules["RPi"] = unittest.mock.MagicMock()
sys.modules["RPi.GPIO"] = unittest.mock.MagicMock()

import service

service.Daemon().press()
