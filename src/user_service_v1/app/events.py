import pika 
import json 
from user_service_v1.app.config import Config, logger


def publish_user_update_event(user_id: str, emails: list, delivery_address: dict):
    logger.info(f"Preparing to publish user update event for user_id={user_id}")
    try:
        connection = pika.BlockingConnection(pika.URLParameters(Config.RABBITMQ_URI))
        channel = connection.channel()
        logger.info("RabbitMQ connection established successfully")

        channel.exchange_declare(exchange=Config.RABBITMQ_QUEUE_NAME, exchange_type="fanout", durable=True)
        logger.info("Declared 'user_events' exchange")
        event = {
                "event": "user.updated",
                "userId": user_id,
                "emails": emails,
                "deliveryAddress": delivery_address
            }

        message = json.dumps(event)
        channel.basic_publish(exchange="", routing_key=Config.RABBITMQ_QUEUE_NAME, body=message)
        logger.info(f"Published user update event to RabbitMQ for user_id={user_id}")

        connection.close()
        logger.info("RabbitMQ connection closed cleanly.")
        
    except Exception as e:
        logger.exception(f"Failed to publish user update event for user_id={user_id}: {e}")
                              
