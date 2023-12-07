import time
from threading import Thread, _shutdown
import requests

count = 0
start_time = time.time()

while count < 50:
    requests.get("https://example.com")
    count += 1

end_time = time.time()

print(f"Seconds elapsed: {end_time - start_time}")