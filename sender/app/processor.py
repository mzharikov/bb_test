import json
from config import settings
from validators import LogRecordSchema


def send_to_queue(channel, queue_name: str, log_record: dict) -> None:
    fields_to_send = {
        key: log_record[key]
        for key in (
            "event_id",
            "match_time",
            "status",
            "game_period",
            "home_score",
            "away_score",
        )
    }
    channel.basic_publish(
        exchange=settings.EXCHANGE_NAME,
        routing_key=queue_name,
        body=json.dumps(fields_to_send),
    )


async def proccess_log_record(
    channel, collection, queue_name: str, log_record: dict
):
    async def db_insert_document() -> None:
        await collection.insert_one(log_record)

    LogRecordSchema.validate(log_record)
    await db_insert_document()
    send_to_queue(channel, queue_name, log_record)
