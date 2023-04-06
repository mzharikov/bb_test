import pika
import asyncio
import time
import json
import logging
import socket
import motor.motor_asyncio
import pika.exceptions
from pydantic import ValidationError
from pymongo import errors
from reader import log_record_generator
from config import settings
from processor import proccess_log_record
from initializer import load_match_config, setup_mq


def send_error(channel, error_queue_name: str, reason: str) -> None:
    channel.basic_publish(
        exchange=settings.EXCHANGE_NAME,
        routing_key=error_queue_name,
        body=json.dumps(
            {
                "reason": reason,
            }
        ),
    )


async def main():
    match_config = load_match_config()
    sports_event_id = match_config["id"]
    queue_name = f"q{sports_event_id}"
    error_queue_name = f"e{sports_event_id}"

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=settings.RABBITMQ_URL)
        )
        channel = connection.channel()

    except pika.exceptions.AMQPConnectionError as amqpe_error:
        logging.error("Could not connect to RabbitMQ server")
        return
    except socket.gaierror:
        logging.error("Could not resolve RabbitMQ server address")
        return

    setup_mq(channel, queue_name, error_queue_name)

    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URL)
        db = client[settings.MONGO_MAIN_DATABASE]
        collection = db[settings.MONGO_EVENT_LOG_COLLECTION]
    except errors.ConnectionFailure as connection_failure:
        send_error(channel, error_queue_name, "db_connection_error")
        logging.error(
            f"Could not connect to MongoDB server. {connection_failure}"
        )
        return

    print("Working. Press CTRL+C for emergency stop")

    try:
        async for log_record in log_record_generator():
            await proccess_log_record(
                channel, collection, queue_name, log_record
            )

    except ValidationError as validation_error:
        send_error(channel, error_queue_name, "validation_error")
        logging.error(f"Task failed: {validation_error}")

    except errors.PyMongoError as db_error:
        send_error(channel, error_queue_name, "db_general_error")
        logging.error(f"DB error occurred: {db_error}")

    except pika.exceptions.AMQPError as amqpe_error:
        logging.error(f"RabbitMQ error occurred: {amqpe_error}")

    finally:
        channel.close()
        connection.close()


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Emergency stop requested...")
