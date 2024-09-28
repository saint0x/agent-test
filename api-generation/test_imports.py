from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TestModel(BaseModel):
    name: str
    value: int

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)