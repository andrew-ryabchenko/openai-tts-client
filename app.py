from config import Configuration
from files import FileManager
from exceptions import FileError, ConfigurationError, InputDataError
from segment import SegmentGenerator
from api import TTSAPI
import sys

class App:

    configuration: Configuration
    file_manager: FileManager
    segment_generator: SegmentGenerator
    tts_api: TTSAPI

    def run(self):

        #Instantiate Configuration class and parse command line arguments
        try:
            self.configuration = Configuration()
        except ConfigurationError as err:
            print(err, file=sys.stderr)
            sys.exit(1)

        #Parse configuration file
        try:
            self.configuration.parse_configuration_file(self.configuration.options.config_file_path)
        except ConfigurationError as err:
            print(err, file=sys.stderr)
            sys.exit(1)

        #Instantiate FileManager object for further file management needs
        try:
            self.file_manager = FileManager()
            #self.file_manager.set("configuration_file", self.configuration.options.config_file_path, "r", encoding="utf-8")
            self.file_manager.set("input_file", self.configuration.options.input_file_path, "r", encoding="utf-8")
            self.file_manager.set("output_file", self.configuration.options.output_file_path, "ab")
        except FileError as err:
            print(err, file=sys.stderr)
            sys.exit(1)
        
        #Instantiate SegmentGenerator and generate segments
        try:
            self.segment_generator = SegmentGenerator(4096, self.file_manager.get("input_file"))
            self.segment_generator.generate_sentences()
            self.segment_generator.generate_segments()
        except InputDataError as err:
            print(err, file=sys.stderr)
            sys.exit(1)
        except BaseException as err:
            print("Unexpected error occured...", err, sep=" ", file=sys.stderr)
            sys.exit(1)

        #Instantiate TTSAPI class
        self.tts_api = TTSAPI(
            self.configuration.option.api["api_key"],
            self.configuration.option.api["voice"],
            self.configuration.option.api["model"],
            self.configuration.option.api["speed"],
            self.configuration.option.api["response_format"]
        )

        #Check viability of the opration which depends on the number of remaining requests current API key can make
        viable = self.tts_api.check_viability(self.segment_generator.num_segments)
        if not viable:
            print(("Current operation is not possible due to the API rate limit constraint.\n"
                   f"Segments to process: {self.segment_generator.num_segments}\n"
                   f"Available requests: {self.tts_api.remaining_requests}"))
            sys.exit(1)

        cost = self.tts_api.estimate_cost(self.segment_generator.len_text)
        print("Approximate cost to perfrom this operation: %.2f\n" % cost)
        uinput = input("Proceed? (y/n): ").lower()

        if (uinput != "y"):
            print("Operation aborted. Bye.")
            sys.exit(0)

        #At this point user has given consent to proceed with the API calls
        



        #Display approximate cost of the tts API call based on data size and 
        #prompt for user's permission to continue
         

if __name__ == "__main__":
    sys.argv = ['app.py', '-i', 'input.txt', '-o', 'outfile.mp3', '-c', 'test.txt']
    App().run()