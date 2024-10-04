from fastapi import FastAPI, WebSocket
import uvicorn
import os
import auth
import chat
import sockets
from honeybadger import honeybadger, contrib
from fastapi.routing import APIRouter
from honeybadger.contrib.fastapi import HoneybadgerRoute

fastapi_config = {
    "title":"RaptChat Service",
    "debug":True,
    "root_path": "/api",
}

honeybadger.configure(api_key="Your project API key")
app = FastAPI(**fastapi_config)
app.include_router(auth.router,prefix="/auth")
app.include_router(chat.router,prefix="/chat")

async def chatsocket_wrapper(websocket: WebSocket, room_id: str):
    try:
        await sockets.chatsocket(websocket, room_id)
    except Exception as e:
        honeybadger.notify(e)
        raise
app.add_api_websocket_route("/chatsocket/{room_id}",chatsocket_wrapper)



if __name__ == "__main__":
    SERVICE_PORT = os.environ.get("SERVICE_PORT")
    uvicorn.run(app="api:app",host="0.0.0.0",port=int(SERVICE_PORT),reload=True)