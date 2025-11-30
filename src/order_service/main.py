from fastapi import FastAPI
from pymongo import MongoClient
from order_service.app.config import Config
from order_service.app.routes import router as order_router
from order_service.app.events import consume_user_update_events
import threading

app = FastAPI(title="Order Service")

# === MongoDB setup ===
client = MongoClient(Config.MONGO_URI)
db = client[Config.DB_NAME]
app.orders_collection = db["orders"]


# === Include routes ===
app.include_router(order_router, prefix="/orders", tags=["orders"])

# === Start RabbitMQ consumer in background thread ===
@app.on_event("startup")
def start_rabbitmq_consumer():
    threading.Thread(target=consume_user_update_events, args=(app,), daemon=True).start()
    print("RabbitMQ consumer thread started.")


