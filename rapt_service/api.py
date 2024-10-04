from fastapi import Depends, FastAPI, Request, WebSocket
from pydantic import UUID4
import uvicorn
import os
import auth
import chat
from depends import authorize, get_db
import sockets
from honeybadger import honeybadger
from config import settings
import models

fastapi_config = {
    "title":"RaptChat Service",
    "debug":True,
    "root_path": "/api",
}

honeybadger.configure(api_key=settings.honeybadger_api_key,environment="production",report_data=True)
app = FastAPI(**fastapi_config)
app.include_router(auth.router,prefix="/auth")
app.include_router(chat.router,prefix="/chat")

async def chatsocket_wrapper(
                        websocket: WebSocket, 
                        room_id: UUID4,
                        user: models.User = Depends(authorize(perm="create_chats")),
                        db: models.Session = Depends(get_db)
                    ):
    try:
        await sockets.chatsocket(websocket, room_id, user=user, db=db)
    except Exception as e:
        honeybadger.notify(e)
        raise
app.add_api_websocket_route("/chatsocket/{room_id}",chatsocket_wrapper)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    honeybadger.context(
        url=str(request.url),
        method=request.method,
        headers=dict(request.headers),
        query_params=dict(request.query_params)
    )
    response = await call_next(request)
    return response


if __name__ == "__main__":
    SERVICE_PORT = os.environ.get("SERVICE_PORT")
    uvicorn.run(app="api:app",host="0.0.0.0",port=int(SERVICE_PORT),reload=True)