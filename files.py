from io import TextIOWrapper
from exceptions import FileError

class FileManager:

    configuration_file: TextIOWrapper
    input_file: TextIOWrapper
    output_file: TextIOWrapper

    def set(self, name: str, path: str, mode: str, encoding: str = None) -> None:
        try:
            file = open(path, mode, encoding=encoding)
            self.__dict__[name] = file
        except PermissionError:
            raise FileError(f"Permission denied: {path}")
        except IOError:
            raise FileError(f"Could not open file: {path}")

    def get(self, name: str) -> TextIOWrapper:
        return self.__dict__[name]
    
    def read(self, name: str, n: int = -1) -> str:
        return self.__dict__[name].read()
    
    def write(self, name: str, data: bytes) -> None:
        file = self.__dict__[name]
        file.write(data)


if __name__ == "__main__":
    #TODO implement unit tests
    fm = FileManager()
    fm.set("configuration_file", "test.txt", "a")
    print(fm.read("configuration_file"))