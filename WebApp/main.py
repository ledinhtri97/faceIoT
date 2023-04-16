from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from AdafruitClient import IoTClient
import uvicorn
import os
import threading
import signal
import time

ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))

app = FastAPI()
iotClient = IoTClient()
uvicornServer = None

app.mount("/static", StaticFiles(directory=os.path.join(ABSOLUTE_PATH, "static")), name="static")
app.mount("/app", StaticFiles(directory=os.path.join(ABSOLUTE_PATH, "app")), name="app")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    global iotClient
    while True:
        try:
            item = iotClient.getQueueData()
            if item is not None:
                data = json.dumps(item)
                # print(data)
                await websocket.send_text(data)
        except Exception as e:
            print("websocket error: ", str(e))
            break
        await asyncio.sleep(1)

# Define a route to receive POST requests.
@app.post("/api/postLEDMessage")
async def postLEDMessage(request: Request):
    global iotClient
    content_type = request.headers.get('Content-Type')
    res = {}
    if content_type is None:
        return 'No Content-Type provided.'
    elif content_type == 'application/json':
        try:
            jsonData = await request.json()
            print("Input: ", jsonData)
            mes = jsonData["data"]
            res["message"] = mes

            iotClient.publishLEDMessage(mes)

        except Exception as e:
            res["error"] = str(e)
    else:
        res["error"] = 'Content-Type not supported.'
    res["timestamp"] = str(time.time())
    return res

@app.post("/api/postNewGuest")
async def postNewGuest(request: Request):
    global iotClient
    content_type = request.headers.get('Content-Type')
    res = {}
    if content_type is None:
        return 'No Content-Type provided.'
    elif content_type == 'application/json':
        try:
            jsonData = await request.json()
            print("New Guest: ", jsonData)
            name = jsonData["name"]
            id = jsonData["id"]
            res["message"] = name + "_" + id

            iotClient.publishNewGuest(name, id)

        except Exception as e:
            res["error"] = str(e)
    else:
        res["error"] = 'Content-Type not supported.'
    res["timestamp"] = str(time.time())
    return res

def signal_handler(sig, frame):
    print("Received SIGINT. Exiting...")
    global iotClient
    iotClient.stop()
    exit(0)

if __name__ == '__main__':

    iotClient.start()
    signal.signal(signal.SIGINT, signal_handler)

    # create a UVicorn config object with your desired settings
    config = uvicorn.Config(app=app, host="127.0.0.1", port=8000, loop="asyncio")
    # create a new server instance using your config object
    uvicornServer = uvicorn.Server(config)

    def run_server():
        # start the server
        uvicornServer.run()
    
    # Start the server in a new thread.
    server_thread = threading.Thread(target=run_server)
    server_thread.start()