from fastapi import FastAPI, WebSocket
import asyncio
import threading
import queue

class WebSocketServer:
    def __init__(self):
        self.app = FastAPI()
        self.message_queue = queue.Queue()
        self.clients = []
        self.start_worker()

    def start_worker(self):
        threading.Thread(target=self.message_worker, daemon=True).start()

    async def websocket_endpoint(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.append(websocket)
        try:
            while True:
                await websocket.receive_text()
        except:
            self.clients.remove(websocket)

    def message_worker(self):
        while True:
            message = self.message_queue.get()
            for client in self.clients:
                asyncio.run(client.send_text(message))

    def report_generated(self, report):
        self.message_queue.put(f"New report generated: {report}")
