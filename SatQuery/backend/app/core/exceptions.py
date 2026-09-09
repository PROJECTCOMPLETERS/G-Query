class SatQueryException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        details=None,
    ):
        self.code = code
        self.message = message
        self.details = details

        super().__init__(message)