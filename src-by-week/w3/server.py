from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List, Dict, Union
from threading import Thread
import asyncio
from pydantic import BaseModel
from starlette.websockets import WebSocket, WebSocketState
from w3.utils.websocket import ConnectionManager
from w3.utils.response_model import ProcessStatus
from w3.utils.database import DB

app = FastAPI()
manager = ConnectionManager()

# start an asynchronous task that will keep broadcasting the process status to all the connected clients
broadcast_continuous = Thread(target=asyncio.run, args=(manager.broadcast_all(),))
broadcast_continuous.start()


# The below endpoint is used to create websocket connection
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # create a websocket connection for a client and assign it to a room
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast message to all the connections/clients in a chatroom
            await websocket.send_text("Websocket connection established Connected")

    except WebSocketDisconnect:
        print("Client disconnected")


# health check API
@app.get("/health")
async def get() -> Dict:
    """
    should send a JSON response in the below format:
    {"status": "ok"}
    """
    res = {"status": "ok"}
    return res


# Below endpoint renders an HTML page
@app.get("/")
async def get() -> HTMLResponse:
    """
    should render the HTML file - index.html when a user goes to http://127.0.0.1:8000/
    """
    with open("index.html", "r", encoding="utf-8") as html_file:
        content = html_file.read()
    return HTMLResponse(content=content)


# Below endpoint to get the initial data
@app.get("/processes")
async def get() -> List[ProcessStatus]:
    """
    Get all the records from the process table and return it using the pydantic model ProcessStatus
    """
    # use DB read_all function to get all the records
    # read_all returns List[Dict]
    db = DB()
    records = db.read_all()

    return [ProcessStatus(**record) for record in records]