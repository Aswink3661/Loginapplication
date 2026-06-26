import logging
from logging.handlers import RotatingFileHandler

import pytest

from src.config.settings import Settings
from src.utils.logger import LoggerFactory, _MANAGED_HANDLER_ATTR


@pytest.fixture(autouse=True)
def cleanup_managed_handlers():
    yield

    root_logger = logging.getLogger()
    for handler in list(root_logger.handlers):
        if getattr(handler, _MANAGED_HANDLER_ATTR, False):
            root_logger.removeHandler(handler)
            handler.close()


def managed_handlers() -> list[logging.Handler]:
    return [
        handler
        for handler in logging.getLogger().handlers
        if getattr(handler, _MANAGED_HANDLER_ATTR, False)
    ]


def test_get_logger_returns_named_logger() -> None:
    factory = LoggerFactory(settings=Settings(LOG_TO_FILE=False))

    logger = factory.get_logger("src.tests.logger")

    assert logger.name == "src.tests.logger"


def test_configure_is_idempotent() -> None:
    factory = LoggerFactory(settings=Settings(LOG_LEVEL="DEBUG", LOG_TO_FILE=False))

    factory.configure()
    factory.configure()

    handlers = managed_handlers()
    assert logging.getLogger().level == logging.DEBUG
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)


def test_file_logging_adds_rotating_file_handler(tmp_path) -> None:
    log_file = tmp_path / "logs" / "app.log"
    factory = LoggerFactory(settings=Settings(LOG_TO_FILE=True), log_file=log_file)

    factory.configure()

    handlers = managed_handlers()
    assert log_file.parent.exists()
    assert any(isinstance(handler, RotatingFileHandler) for handler in handlers)
