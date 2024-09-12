from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uvicorn
import os
import models
import auth
import chat
from config import DATABASE_URL,logger
from depends import get_db

fastapi_config = {
    "title":"RaptChat Service",
    "debug":True,
    "root_path": "/api",
}

app = FastAPI(**fastapi_config)
app.include_router(auth.router,prefix="/auth")
app.include_router(chat.router,prefix="/chat")

if __name__ == "__main__":
    SERVICE_PORT = os.environ.get("SERVICE_PORT")
    uvicorn.run(app="api:app",host="0.0.0.0",port=int(SERVICE_PORT),reload=True)