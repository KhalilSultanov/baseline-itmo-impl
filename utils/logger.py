import os
from aiologger import Logger
from aiologger.formatters.base import Formatter
from aiologger.handlers.files import AsyncFileHandler
from aiologger.levels import LogLevel


async def setup_logger():
    """Конфигруация асинхронного логгера и создание лог-файла"""

    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)

    logger = Logger(name="api_logger")

    formatter = Formatter(
        fmt="{asctime} | {levelname} | {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )

    file_handler = AsyncFileHandler(
        filename=os.path.join(log_directory, "api.log"),
        mode="a",
        encoding="utf-8",
    )
    file_handler.formatter = formatter

    logger.add_handler(file_handler)

    logger.level = LogLevel.INFO

    return logger
