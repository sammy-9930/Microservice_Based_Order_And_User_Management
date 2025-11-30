from fastapi import FastAPI
from pymongo import MongoClient
from user_service_v2.app.config import Config
from user_service_v2.app.routes import router

app = FastAPI(title="User Service V2")

client = MongoClient(Config.USER_SERVICE_MONGO_URI)
db = client[Config.USER_SERVICE_DB]
app.users_collection = db["users"]

app.include_router(router, prefix="/users", tags=["users"])

@app.get("/")
async def root():
    return {"message" : "User Service V2 is running"}






