class InputDataError(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ConfigurationError(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class FileError(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class APIError(BaseException):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)