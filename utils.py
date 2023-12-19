from io import TextIOWrapper
from threading import Semaphore
import time

def check_eof(file: TextIOWrapper) -> True:

    current_file_pos = file.tell()
    c = file.read(1)

    if (not c):
        return True
    
    file.seek(current_file_pos)

    return False

def semaphore_wrapper(f):
    """Decorator function that aquires and releases semaphore."""
    
    def wrapper(*args, **kwargs):
        semaphore = kwargs["semaphore"]
        semaphore.acquire()
        f(*args, **kwargs)
        semaphore.release()
    
    return wrapper

def confirm_operation() -> bool:
    """Returns boolean value that represents whether
    the user confirms the tts conversion at the estimated cost."""

    uinput = input("Would you like to proceed? (y/n): ")
    
    return uinput.lower().strip() == "y"

if __name__ == "__main__":
    @semaphore_wrapper
    def f(**kwargs):
        print("Inside the function")
        time.sleep(1)
        
    semaphore = Semaphore(1)
    
    for _ in range(10):
        f(semaphore = semaphore)