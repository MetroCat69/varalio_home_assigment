import logging
from typing import Optional
from logging import Logger


def get_logger(logger_name: Optional[str] = None) -> Logger:
    return logging.getLogger(logger_name)


def log_error(
    logger: Logger,
    message: str,
    error: Exception,
    context: Optional[dict] = None,
) -> None:
    logger.error(
        f"{message}: {error}",
        extra={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
        },
    )
