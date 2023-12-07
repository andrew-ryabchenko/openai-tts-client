from threading import Thread, Semaphore
from result import EnumeratedByteSegments

class ThreadManager:

    _total_threads = 0
    result_container: EnumeratedByteSegments
    semaphore: Semaphore
    segments: [str]
    max_threads: int

    def __init__(self, max_threads: int, worker, 
                 result_container: EnumeratedByteSegments,
                 segments: [str]) -> None:
        self.semaphore = Semaphore(value=max_threads)
        self.result_container = result_container
        self.worker = worker
        self.segments = segments
        self.max_threads = max_threads

    def run(self):
        threads = []
        for i in range(0, len(self.segments)):
            segment = self.segments[i]
            thread  = Thread(target=self._worker_function, args=(segment, i,))
            thread.start()
            threads.append(thread)

        #Wait for all threads to complete
        for thread in threads:
            thread.join()

    def _worker_function(self, data: str, order_num: int):

        #Aquire semaphore
        self.semaphore.acquire()

        #It is assumed that total number of running threads wont be larger that the allowed upper limit
        self._total_threads += 1
        assert self._total_threads <= self.max_threads, (f"Error: Total running threads: {self._total_threads}\n"
                                                         f"Max number of running threads: {self.max_threads}")

        #Run worker function and collect the result
        result = self.worker(data)
        self._total_threads -= 1

        #Release semaphore
        self.semaphore.release()

        #Save result in the result container
        self.result_container[order_num] = result

if __name__ == "__main__":
    #Testing
    import requests

    def worker_function(data):
        response = requests.get("https://example.com")
        return response.text
    
    segments = ["hello" for _ in range(100)]

    result_container = EnumeratedByteSegments()

    tm = ThreadManager(10, worker_function, result_container, segments)
    tm.run()
    print(tm)
    print(tm.run)
    failed_requests = 0
    successful_requests = 0

    for key in result_container.keys():
        value = result_container[key]
        if not value:
            failed_requests += 1
        else:
            successful_requests += 1

    print(f"Failed requests: {failed_requests}")
    print(f"Succesfull requests: {successful_requests}")