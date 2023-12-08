from threading import Semaphore
import httpx
from exceptions import APIError

API_KEY = "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"

class TTSAPI:

    API_ENDPOINT: str = "https://api.openai.com/v1/audio/speech"
    api_key: str
    voice: str
    response_format: str
    speed: str
    model: str
    limit_requests: int
    remaining_requests: int
    reset_requests: str

    def __init__(self, api_key: str, voice: str, model: str, speed: str, respose_format: str) -> None:
        
        self.api_key = api_key
        self.voice = voice
        self.model = model
        self.speed = speed
        self.response_format = respose_format

    def get_limits(self):
        self.limit_requests,
        self.remaining_requests,
        self.reset_requests = self.__get_limits()
        
    def __get_limits(self):
        body = {
            "model": self.model,
            "voice": self.voice,
            "input": "The."
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        response = httpx.post(self.API_ENDPOINT, headers=headers, json=body)

        if response.status_code != 200:
            raise APIError(f"OpenAI server responded with an error:\n{response.text}")
        
        return (int(response.headers.get("x-ratelimit-limit-requests")),
                int(response.headers.get("x-ratelimit-remaining-requests")),
                response.headers.get("x-ratelimit-reset-requests"),)

    def check_viability(self, num_segments: int) -> bool:
        return num_segments <= self.remaining_requests 
    
    def estimate_cost(self, len_text: int) -> float:
        if self.model == "tts-1":
            return len_text / 1000 * 0.015
        return len_text / 1000 * 0.03

    def create(self, data: str) -> bytes:

        body = {
            "model": self.model,
            "voice": self.voice,
            "input": data
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        response = httpx.post(self.API_ENDPOINT, headers=headers, json=body)

        if response.status_code != 200:
            raise APIError(f"OpenAI server responded with an error:\n{response.text}")

        return response.content
