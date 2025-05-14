class InternalError(Exception):
    """Exception raised for internal errors. Signifies a bug in the implementation."""
    def __init__(self, message):
        super().__init__(message)
