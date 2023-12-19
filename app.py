from exceptions import ConfigurationError, FileError, InputDataError, APIError
from argparse import ArgumentParser, Namespace
from os import path
from threading import Semaphore
from configuration import Configuration
from file_manager import FileManager
from segment_generator import SegmentGenerator
from api import ApiCall
from utils import confirm_operation
import sys
                
class App(ArgumentParser):

    debug: List[str]
    configuration: Configuration
    file_manager: FileManager
    segment_generator: SegmentGenerator

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
        """Implements the top-level logic of the program
        and coordinates data flow between components."""

        try:
            #Instantiate configuration object
            self.configuration = self._parse_args()
        except ConfigurationError as err:
            print(err, file=sys.stderr)
            sys.exit(1)
            
        try:
            #Instantiate FileManager class
            infile = self.configuration.option.input_file_path
            outfile = self.configuration.option.output_file_path
            
            self.file_manager = FileManager()
            self.file_manager.set("input_file", infile, "r", "utf-8")
            self.file_manager.set("output_file", outfile, "ab")
        except FileError as err:
            print(err, file=sys.stderr)
            sys.exit(2)
            
        try:
            #Generate segments
            infile = self.configuration.option.input_file_path
            
            self.segment_generator = SegmentGenerator(4096, infile)
            self.segment_generator.generate_sentences()
            self.segment_generator.generate_segments()
        except InputDataError as err:
            print(err, file=sys.stderr)
            sys.exit(3)
            
        try:
            ApiCall.api_key = self.configuration.options.config_file.api_key
            ApiCall.model = self.configuration.options.config_file.model
            ApiCall.voice = self.configuration.options.config_file.voice
            ApiCall.response_format = self.configuration.options.config_file.response_format
            ApiCall.speed = int(self.configuration.options.config_file.speed)
    
            max_threads = int(self.configuration.options.config_file.max_threads)
            call_threads = []
            semaphore = Semaphore(value=max_threads)
            segments = self.segment_generator.segments
            lentext = self.segment_generator.len_text
            #Estimate the cost of the operation and prompt user for confimation
            estimated_cost = ApiCall.estimate_cost(lentext)
            
            #Inform the user of estimated operation costs
            print("The estimated cost of this conversion is $%.2f" % estimated_cost)
            
            #Exit the program if user does not wish to proceed
            if not confirm_operation():
                sys.exit(0)
            
            #Create separate ApiCall for each input data segment
            for segment in segments:
                api_call = ApiCall(segment, semaphore)
                #Perform the api call in a separate thread of control
                api_call.start()
                #Add thread to the threads list
                call_threads.append(api_call)
                
            #Consequtively joins every thread collecting audio data
            for api_call in call_threads:
                api_call.join()
                if api_call.error:
                    #TODO implement API error logging
                    pass
                else:
                    #Write speech segment to the output file
                    self.file_manager.write("output_file", api_call.speech)
                    
        except BaseException as err:
            print(err, file=sys.stderr)
            sys.exit(3)
            
                