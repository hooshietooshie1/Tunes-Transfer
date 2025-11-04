class ClassicException(Exception):
    """
    "Handle all errors gracefully."
        - Sun Tzhu (probably)
    """
    def __init__(self, msg: str, err_code: int = None):
        super().__init__(msg)
        # AUTHENTICATION FAILURE: 90
        # UNKNOWN FAILURE: 99
        # USER-error FAILURE: 30
        # BASE FAILURE: 10 / None

        self.code = err_code
        self.message = msg

    def __str__(self):
        code_str = f"[error code {self.code}]" if self.code else ""
        return f"CaughtError {code_str}: {self.message}"
