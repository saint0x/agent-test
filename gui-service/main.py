import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .websocket_server import WebSocketServer
from .message_broker import MessageBroker

# Create an instance of the FastAPI app
app = FastAPI()

# Create instances of WebSocketServer and MessageBroker
ws_server = WebSocketServer()
message_broker = MessageBroker()

# Include the WebSocket routes
app.websocket("/ws")(ws_server.websocket_endpoint)

# Pydantic model for report generation
class Report(BaseModel):
    title: str
    content: str

# Endpoint to generate a report
@app.post("/reports/")
def generate_report(report: Report):
    try:
        # Logic to generate the report
        message_broker.notify_report_generated(report.title)
        return {"message": "Report generated successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Start the FastAPI server
def start_server():
    try:
        uvicorn.run(app, host='127.0.0.1', port=8000)
        print("🚀 Server is running at http://127.0.0.1:8000/ws")
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")

if __name__ == '__main__':
    start_server()