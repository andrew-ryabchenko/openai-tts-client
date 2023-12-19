from collections.abc import Callable, Iterable, Mapping
from typing import Any
from threading import Semaphore
import httpx
from exceptions import APIError
from threading import Thread
import openai
from time import sleep

class ApiCall(Thread):

    #API options that will be shared among all calls
    API_ENDPOINT: str = "https://api.openai.com/v1/audio/speech"
    api_key: str
    voice: str
    response_format: str
    speed: float
    model: str
    
    semaphore: Semaphore

    def __init__(self, data: str, semaphore: Semaphore,
                 group: None = None, 
                 target: Callable[..., object] | None = None,
                 name: str | None = None, args: Iterable[Any] = ..., 
                 kwargs: Mapping[str, Any] | None = None, *, 
                 daemon: bool | None = None) -> None:
        #Text data for current API call
        self.data = data
        #Semaphore instance for thread synchronization
        self.semaphore = semaphore
        #Call parent class constructor
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        
    def get_limits():
        ApiCall.limit_requests,
        ApiCall.remaining_requests,
        ApiCall.reset_requests = ApiCall.__get_limits()
        
    def __get_limits():
        body = {
            "model": ApiCall.model,
            "voice": ApiCall.voice,
            "input": "The."
        }
        headers = {
            "Authorization": f"Bearer {ApiCall.api_key}"
        }
        response = httpx.post(ApiCall.API_ENDPOINT, headers=headers, json=body)

        if response.status_code != 200:
            raise APIError(f"OpenAI server responded with an error:\n{response.text}")
        
        return (int(response.headers.get("x-ratelimit-limit-requests")),
                int(response.headers.get("x-ratelimit-remaining-requests")),
                response.headers.get("x-ratelimit-reset-requests"),)

    def check_viability(num_segments: int) -> bool:
        return num_segments <= ApiCall.remaining_requests 
    
    def estimate_cost(len_text: int) -> float:
        if ApiCall.model == "tts-1":
            return len_text / 1000 * 0.015
        return len_text / 1000 * 0.03

    def check_rpd(self, headers) -> bool:
        """Check whether the RPD (requests per day) account limit has exceeded."""

        limit_requests = int(headers["x-ratelimit-limit-requests"])
        remaining_requests = int(headers["x-ratelimit-remaining-requests"])
        if limit_requests == 200 and remaining_requests < 1:
            #Free tier account. RPD limit exceeded.
            return True
        
        return False
      
    def run(self) -> None:
        
        client = openai.OpenAI(
            api_key=ApiCall.api_key
        )
        
        try:
            self.semaphore.acquire()
            response = client.audio.speech.create(
                input=self.data,
                model=ApiCall.model,
                voice=ApiCall.voice,
                response_format=ApiCall.response_format,
                speed=ApiCall.speed,
            )
            
            self.error = False
            self.status_code = 200
            
            self.speech = response.read()

        #Rate limit exception handler
        except openai.RateLimitError as err:
            self.semaphore.release()
            headers = err.response.headers
            if self.check_rpd(headers):
                #RPD limit is exceeded.
                self.error = True
                self.status_code = err.status_code
                self.response = err.response
                self.speech = None
            else:
                #RPM is likely exceeded. Re-try again in 60s.
                print("RPM limit exceeded. Re-trying in 60s.")
                sleep(60.0)
                self.run(self.semaphore)
                
        #All other types of API or network related exceptions   
        except openai.APIError as err:
            self.semaphore.release()
            self.error = True
            self.status_code = err.status_code
            self.response = err.response
            self.speech = None

if __name__ == "__main__":
    from segment_generator import SegmentGenerator
    
    API_KEY_TIER1 = "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"
    
    ApiCall.api_key = API_KEY_TIER1
    ApiCall.model = "tts-1"
    ApiCall.voice = "onyx"
    ApiCall.response_format = "mp3"
    ApiCall.speed = 1.0
    
    call_threads = []
    
    input_file_path = "testing/input.txt"
    
    infile = open(input_file_path,encoding="utf-8")
    
    sg = SegmentGenerator(500, infile)

    sg.generate_sentences()
    sg.generate_segments()
    print(sg.num_segments)
    for segment in sg.segments:
        api_call = ApiCall(segment)
        api_call.start()
        call_threads.append(api_call)
        
    with open("testing/output.mp3", "+ab") as outfile:
        for api_call in call_threads:
            api_call.join()
            if not api_call.error:
                outfile.write(api_call.speech)
            else:
                print(f"Status code: {api_call.status_code}\nMessage: {api_call.response}")
