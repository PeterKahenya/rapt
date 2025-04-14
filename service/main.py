from fastapi import FastAPI
import uvicorn
import os
from api import auth,chat
from honeybadger import honeybadger
from config import settings

fastapi_config = {
    "title":"RaptChat Service",
    "debug":True,
    "root_path": "/api",
}

honeybadger.configure(api_key=settings.honeybadger_api_key,environment="production",report_data=True)
app = FastAPI(**fastapi_config)
app.include_router(auth.router,prefix="/auth")
app.include_router(chat.router,prefix="/chat")

if __name__ == "__main__":
    SERVICE_PORT = os.environ.get("SERVICE_PORT")
    uvicorn.run(app="app",host="0.0.0.0",port=int(SERVICE_PORT),reload=True)