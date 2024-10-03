from fastapi import FastAPI
import uvicorn
import os
import auth
import chat
import sockets

fastapi_config = {
    "title":"RaptChat Service",
    "debug":True,
    "root_path": "/api",
}

app = FastAPI(**fastapi_config)
app.include_router(auth.router,prefix="/auth")
app.include_router(chat.router,prefix="/chat")
app.add_api_websocket_route("/chatsocket/{room_id}",sockets.chatsocket)

if __name__ == "__main__":
    SERVICE_PORT = os.environ.get("SERVICE_PORT")
    uvicorn.run(app="api:app",host="0.0.0.0",port=int(SERVICE_PORT),reload=True)