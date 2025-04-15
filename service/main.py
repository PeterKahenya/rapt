import os
from fastapi import FastAPI, Request
import uvicorn
from api import auth,chat
from honeybadger import honeybadger
from config import settings
from sockets.chat_socket import chatsocket_wrapper


fastapi_config = {
    "title":"RaptChat Service",
    "debug":True,
    "root_path": "/api",
}

honeybadger.configure(api_key=settings.honeybadger_api_key,environment="production",report_data=True)
app = FastAPI(**fastapi_config)
app.include_router(auth.router,prefix="/auth")
app.include_router(chat.router,prefix="/chat")
app.add_api_websocket_route("/chatsocket/{room_id}",chatsocket_wrapper)

@app.middleware("http")
async def log_request_context(request: Request, call_next):
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
    uvicorn.run(app="app",host="0.0.0.0",port=int(SERVICE_PORT),reload=True)