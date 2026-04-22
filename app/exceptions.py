class AppException(Exception):
    def __init__(self, code: str, message: str, field: str = None, status_code: int = 400, data: dict = None):
        self.code = code
        self.message = message
        self.field = field
        self.status_code = status_code
        self.data = data
