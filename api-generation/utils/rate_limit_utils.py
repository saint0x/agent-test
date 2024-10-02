from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

class RateLimiter:
    def __init__(self):
        self.limiter = Limiter(key_func=get_remote_address)

    def setup_limiter(self, app):
        app.state.limiter = self.limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    def rate_limit(self, limit_string):
        return self.limiter.limit(limit_string)