from exceptions import ConfigurationError
from io import TextIOWrapper
from argparse import ArgumentParser, Action, Namespace
from os import path
import configparser
from collections import defaultdict

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
                return 10
            case _:
                return None


class PathNormalizer(Action):
        def __call__(self, parser: ArgumentParser, namespace: Namespace, values: str | None, option_string: str | None = None) -> None:
            file_path = path.normcase(values[0])
            file_path = path.normpath(file_path)
            file_path = path.abspath(file_path)
            match option_string:
                case "-i":
                    if not self.check_file(file_path):
                        raise ConfigurationError(f"Input file does not exist: {file_path}")
                    setattr(namespace, "input_file_path", file_path)
                case "-o":
                    setattr(namespace, "output_file_path", file_path)
                case "-c":
                    if not self.check_file(file_path):
                        raise ConfigurationError(f"Configuration file does not exist: {file_path}")
                    setattr(namespace, "config_file_path", file_path)

        
        def check_file(self, file_path) -> bool:
            return path.exists(file_path) and path.isfile(file_path)
                
class Configuration(ArgumentParser):
    
    api_key: str
    options: Namespace

    def __init__(self, debug: list = None) -> None:
        
        super().__init__(description="Convert text to speech using OpenAI API.")
        
        self.add_argument("-i", nargs=1, type=str, action=PathNormalizer,
                          required=True, metavar="<input file>", help="path to a text file with input data")
        self.add_argument("-o", nargs=1, type=str, action=PathNormalizer,
                          required=True, metavar="<output file>", help="path to an output .mp3 file (automatically created)")
        self.add_argument("-c", nargs=1, type=str, action=PathNormalizer, metavar="<config file>",
                          help="path to a text file containing various configurations and API key")
        if debug:
            self.options = self.parse_args(debug)
        else:
            self.options = self.parse_args()

        if "config_file_path" not in self.options:
            config_file_path = path.abspath(DEFAULT_CONFIG_NAME)
            if path.exists(config_file_path) and path.isfile(config_file_path):
                setattr(self.options, "config_file_path", config_file_path)
            else:
                raise ConfigurationError((f"Default configuration file '{DEFAULT_CONFIG_NAME}' "
                                           "must be present in a current working directory."))

    def parse_configuration_file(self, config_file_path: str) -> None:

        api_configurations = DefaultAPIConfigurations()
        setattr(self.options, "api", api_configurations)

        config = configparser.ConfigParser()

        try:
            config.read(config_file_path)
            for key in config["api"].keys():
                self.options.api[key] = config["api"][key]
            if not self.options.api["api_key"]:
                raise ConfigurationError("API key is missing. Add API key to the configuration file.")
        except configparser.MissingSectionHeaderError:
            raise ConfigurationError("Malformed configuration file. Add '[api]' section header at the top of the file.")

if __name__ == "__main__":
    #TODO test with various invalid cmd arguments
    cfg = Configuration(debug = [])
    # print(cfg.options.input_file_path)
    # print(cfg.options.output_file_path)
