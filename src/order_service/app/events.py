import json
import pika
import threading
from typing import Any, Dict, List, Optional
from order_service.app.config import Config, logger

def create_rabbitmq_channel() -> pika.adapters.blocking_connection.BlockingChannel:
    """
    Creates and returns a RabbitMQ channel using the configuration settings.
    Automatically retries if the broker is temporarily unavailable.
    """
    logger.info("Creating RabbitMQ connection...")
    try:
        params = pika.ConnectionParameters(
            host='rabbitmq',
            port=5672,
            credentials=pika.PlainCredentials(Config.RABBITMQ_USERNAME, Config.RABBITMQ_PASSWORD),
            heartbeat=600,
            blocked_connection_timeout=300,
            connection_attempts=10,
            retry_delay=5,
        )
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=Config.RABBITMQ_QUEUE_NAME, durable=True)
        logger.info(f"Connected to RabbitMQ and declared queue '{Config.RABBITMQ_QUEUE_NAME}'")
        return channel
    except Exception as e:
        logger.exception(f"Failed to create RabbitMQ channel: {e}")
        raise


def consume_user_update_events(app) -> None:
    """
    Consumes user update events from RabbitMQ and updates orders in MongoDB.

    Steps:
    1. Connects to RabbitMQ.
    2. Listens on the queue for user update messages.
    3. When a message arrives, updates orders matching the userId.
    4. Acknowledges the message.
    """
    logger.info("Starting RabbitMQ consumer thread for user update events...")
    channel = create_rabbitmq_channel()

    def callback(ch: Any, method: Any, properties: Any, body: bytes) -> None:
        try:
            event = json.loads(body)
            user_id: str = event.get("userId")
            emails: Optional[List[str]] = event.get("emails")
            delivery_address: Optional[str] = event.get("deliveryAddress")

            if not user_id:
                logger.warning("Received event without userId; skipping message.")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            update_fields: Dict[str, Any] = {}
            if emails:
                update_fields["emails"] = emails
            if delivery_address:
                update_fields["deliveryAddress"] = delivery_address

            # Access MongoDB from FastAPI app context
            orders_collection = app.orders_collection
            result = orders_collection.update_many({"userId": user_id}, {"$set": update_fields})

            logger.info(f"Updated {result.modified_count} order(s) for user {user_id}")
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.exception(f"Error processing event: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(
        queue=Config.RABBITMQ_QUEUE_NAME,
        on_message_callback=callback,
        auto_ack=False,
    )

    logger.info("RabbitMQ consumer started. Waiting for user update events...")
    channel.start_consuming()