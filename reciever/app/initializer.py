from pathlib import Path
import json
from config import settings


def load_match_config() -> dict:
    event_file = str(
        Path(__file__).parent.parent
        / "match_config"
        / settings.MATCH_CONFIG_FILE_NAME
    )
    with open(event_file) as f:
        data = f.read()
    return json.loads(data)


def setup_mq(channel, queue_name: str, error_queue_name: str):
    exchange_name = settings.EXCHANGE_NAME
    channel.exchange_declare(exchange=exchange_name, exchange_type="direct")

    channel.queue_declare(queue=queue_name)
    channel.queue_bind(queue=queue_name, exchange=exchange_name)

    channel.queue_declare(queue=error_queue_name)
    channel.queue_bind(queue=error_queue_name, exchange=exchange_name)
