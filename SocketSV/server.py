from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, status
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://14.225.254.142:2024/${client_id}`);
            console.log(`ws://14.225.254.142:2024/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.list_id: list[int] = []

    async def connect(self, websocket: WebSocket, client_id: int):
        await websocket.accept()
        self.list_id.append(client_id)
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        check = manager.active_connections.index(websocket)
        self.active_connections.remove(websocket)
        print('Remove ', self.list_id[check])
        del self.list_id[check]
        

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self,websocket: WebSocket, message: str):
        print('List id: ', self.list_id)
        try:
            for connection in self.active_connections:
                if connection == websocket:
                    continue
                index = manager.active_connections.index(connection)
                check = manager.active_connections.index(websocket)

                if self.list_id[index] ==self.list_id[check]:
                    await connection.send_text(message)
        except Exception as e:
            print(e)


manager = ConnectionManager()


@app.get("/")
async def get():
    return FileResponse("./html/config .html", media_type="text/html")

@app.post("/{id}")
async def dataEsp(request: Request, id: int):
    data = await request.json()
    data = {
        'data': data
    }
    if id not in manager.list_id:
        return JSONResponse(content=data, status_code=status.HTTP_400_BAD_REQUEST)
    try:
        for connection in manager.active_connections:
            index = manager.active_connections.index(connection)
            if manager.list_id[index] == id:
                print(str(data))
                await connection.send_text(str(data))
    except Exception as e:
        return JSONResponse(content=data, status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(content=data, status_code=status.HTTP_200_OK)

@app.websocket("/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(websocket, '{'+'"data": "{}"'.format(data)+'}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(websocket, f"Client #{client_id} left the chat")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=2024, 
        ws_ping_interval=10, 
        ws_ping_timeout=10, 
        log_level="info"
    )
