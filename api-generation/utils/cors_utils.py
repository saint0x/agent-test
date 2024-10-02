from fastapi.middleware.cors import CORSMiddleware

class CORSConfig:
    def __init__(self, app):
        self.app = app
        self.setup_cors()

    def setup_cors(self):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Allows all origins
            allow_credentials=True,
            allow_methods=["*"],  # Allows all methods
            allow_headers=["*"],  # Allows all headers
        )