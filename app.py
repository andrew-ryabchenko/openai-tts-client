from exceptions import ConfigurationError
from argparse import ArgumentParser, Namespace
from os import path
from configuration import Configuration
import configparser
                
class App(ArgumentParser):

    debug: List[str]
    configuration: Configuration

    def __init__(self, debug: List[str] = None) -> None:
        
        self.debug = debug

        super().__init__(description="Convert text to speech using OpenAI API.")
        
        self.add_argument("-i", nargs=1, type=str, action='store', dest="input_file_path",
                          required=True, metavar="<input file>", help="path to a text file with input data")
        self.add_argument("-o", nargs=1, type=str, action='store', dest="output_file_path",
                          required=True, metavar="<output file>", help="path to an output .mp3 file (automatically created)")
        self.add_argument("-c", nargs=1, type=str, action='store', metavar="<config file>", dest="config_file_path",
                          help="path to a text file containing various configurations and API key")

    def _parse_args(self, debug: List[str] = None) -> Namespace:
        """Parses user-supplied command line arguments to produce 
        'Namespace' object containing argument values."""

        #List of arguments is provided (usually during testing)
        if debug:
            return self.parse_args(self.debug)
        #Arguments are taken directly from sys.argv
        return self.parse_args()

    def run(self):
        """Implements top-level logic of the program
        and coordinates data flow between components."""

        #Instantiate configuration object
        self.configuration = self._parse_args()
