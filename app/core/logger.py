import logging
from typing import Literal

type LogLevel = Literal[
    "NOTSET",
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]


def setup_logging(
    log_level: LogLevel = "WARNING",
    log_file_path: str | None = None,
) -> None:
    log_format = "[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(funcName)s:%(lineno)d]: %(message)s"
    logger_handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file_path:
        logger_handlers.append(logging.FileHandler(log_file_path))

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=logger_handlers,
    )
