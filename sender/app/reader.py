import asyncio
import json
import logging
from pathlib import Path
from random import randrange
import aiofiles
from config import settings


async def log_record_generator():
    log_file = str(
        Path(__file__).parent.parent / "log_files" / settings.LOG_FILE_NAME
    )
    async with aiofiles.open(log_file, mode="r") as f:
        contents = await f.read()
    try:
        if not contents.strip().startswith("["):
            raise Exception
        for log_record in json.loads(contents):
            yield log_record
            if settings.THROTTLE_INPUT:
                await asyncio.sleep(randrange(1, 3))

    except Exception:
        logging.error(
            "Unsupported log file format. Should be JSON array of objects"
        )
