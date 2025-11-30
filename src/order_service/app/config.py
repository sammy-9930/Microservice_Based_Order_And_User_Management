import os
import logging 
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

logger = logging.getLogger("order_service")

class Config:
    MONGO_URI = os.getenv("ORDER_MONGO_URI")
    DB_NAME= os.getenv("ORDER_DB")
    RABBITMQ_QUEUE_NAME = os.getenv("RABBITMQ_QUEUE_NAME")
    RABBITMQ_URI = os.getenv("RABBITMQ_URI")
    RABBITMQ_USERNAME = os.getenv("RABBITMQ_USERNAME")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")