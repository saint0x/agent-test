import uvicorn
from fastapi import FastAPI
from .websocket_server import WebSocketServer
from .message_broker import MessageBroker

# Create an instance of the FastAPI app
app = FastAPI()

# Create instances of WebSocketServer and MessageBroker
ws_server = WebSocketServer()
message_broker = MessageBroker()

# Include the WebSocket routes
app.websocket("/ws")(ws_server.websocket_endpoint)

# Function to notify subscribers when a report is generated
def notify_report_generated(report):
    message_broker.notify_subscribers(report)
    message_broker.notify_all()  # Notify all subscribers

# Start the FastAPI server
def start_server():
    try:
        uvicorn.run(app, host='127.0.0.1', port=8000)
        print("🚀 Server is running at http://127.0.0.1:8000/ws")
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")

if __name__ == '__main__':
    start_server()