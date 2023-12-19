from argparse import Namespace
from collections import defaultdict
from os import path
from exceptions import ConfigurationError
import configparser

DEFAULT_CONFIG_NAME = "config.txt"

class DefaultAPIConfigurations(defaultdict):
    def __missing__(self, key) -> str | None:
        match key:
            case "voice":
                return "alloy"
            case "response_format":
                return "mp3"
            case "speed":
                return "1.0"
            case "model":
                return "tts-1"
            case "max_threads":
                return "10"
            case _:
                return None

class Configuration:

    options: Namespace

    def __init__(self, namespace: Namespace) -> None:

        self.options = namespace

        #Check if path to config file was supplied, otherwise 
        #set 'config_file_path' value to the default one.
        if "config_file_path" not in self.options:
            config_file_path = path.abspath(DEFAULT_CONFIG_NAME)
            setattr(self.options, "config_file_path", config_file_path)

        #Normalize paths
        self.options.input_file_path = self._normalize_path(self.options.input_file_path)
        self.options.output_file_path = self._normalize_path(self.options.output_file_path)
        self.options.config_file_path = self._normalize_path(self.options.config_file_path)

        #Verify validity of paths. 

        #Note: Output file path validity is not verified 
        #because it will be opened for appending and automatically 
        #created if does not exist.
        if  not self._check_file(self.options.input_file_path):
            raise ConfigurationError(f"Input file does not exist: {self.options.input_file_path}")
        
        if  not self._check_file(self.options.config_file_path):
            raise ConfigurationError(f"Configuration file does not exist: {self.options.config_file_path}")
        
        #Parse configuration file
        self._parse_configuration_file()

    def _check_file(self, file_path: str) -> bool:
        """Checks if 'path' represents an existing file in the filesystem."""
        return path.exists(file_path) and path.isfile(file_path)

    def _normalize_path(self, file_path: str) -> str:
        """Normalizes path and returns it's absolute version."""

        file_path = path.normcase(file_path)
        file_path = path.normpath(file_path)
        file_path = path.abspath(file_path)
        
        return file_path

    def _parse_configuration_file(self) -> None:
        """Parses configuration file and copies config options
          into the 'options' namespace as a dictionary of key value pairs."""

        api_configurations = DefaultAPIConfigurations()
        setattr(self.options, "config_file", api_configurations)

        config = configparser.ConfigParser()

        try:
            config.read(self.config_file_path)
            for key in config["api"].keys():
                self.options.api[key] = config["api"][key]
            if not self.options.api["api_key"]:
                raise ConfigurationError("API key is missing. Add API key to the configuration file.")
        except configparser.MissingSectionHeaderError:
            raise ConfigurationError("Malformed configuration file. Add '[api]' section header at the top of the file.")
        except IOError:
            raise ConfigurationError(f"Error occurred when attempting to read configuratoon file: {self.config_file_path}.")