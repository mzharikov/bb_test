import pika
import json
import logging
import socket
import pika.exceptions
from config import settings
from processor import EventProcessor
from initializer import load_match_config, setup_mq


def main():
    match_config = load_match_config()
    sports_event_id = match_config["id"]
    processer = EventProcessor(sports_event_id)
    queue_name = f"q{sports_event_id}"
    error_queue_name = f"e{sports_event_id}"

    def process_succuess(ch, method, properties, body):
        processer.update(json.loads(body))

    def process_error(ch, method, properties, body):
        processer.fail(json.loads(body).get("reason"))

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

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=process_succuess,
        auto_ack=True,
    )

    channel.basic_consume(
        queue=error_queue_name,
        on_message_callback=process_error,
        auto_ack=True,
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Terminated")
    finally:
        channel.close()
        connection.close()


if __name__ == "__main__":
    main()
