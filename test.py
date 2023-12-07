from typing import Any
from os import path
from configparser import ConfigParser

config = ConfigParser()

config.read("test.txt")

print(config)