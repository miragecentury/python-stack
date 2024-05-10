"""

"""

import logging
import sys

import structlog
from structlog.typing import Processor
from .utils import add_open_telemetry_spans, add_worker_pid, rename_event_key
from .filters import StdoutFilter, StderrFilter


def _clean_previous_handlers():
    """Clean Loggers from uvicorn, gunicorn and previous"""
    for _log in [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "gunicorn",
        "gunicorn.access",
        "gunicorn.error",
        "asyncio",
    ]:
        # Clear the log handlers for uvicorn loggers, and enable propagation
        # so the messages are caught by our root logger and formatted correctly
        # by structlog
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True

    # Clean Previous Handler
    while logging.getLogger().hasHandlers():
        logging.getLogger().removeHandler(logging.getLogger().handlers[0])


def _configure_shared_processors(json_logs: bool) -> list[Processor]:
    """Build the processors list"""
    # Define common processors
    _shared_processors = [
        # structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.contextvars.merge_contextvars,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        add_open_telemetry_spans,
    ]

    # Append specifics processors for json format
    if json_logs:
        _shared_processors.append(add_worker_pid)
        # We rename the `event` key to `message` only in JSON logs, as Datadog looks
        # for the `message` key but the pretty ConsoleRenderer looks for `event`
        _shared_processors.append(rename_event_key)
        # Format the exception only for JSON logs, as we want to pretty-print them when
        # using the ConsoleRenderer
        _shared_processors.append(structlog.processors.format_exc_info)

    return _shared_processors


def configure_logging(json_logs: bool = False, log_level: int = logging.INFO):
    """Use structlog to define logging format and utils"""

    # Clean
    _clean_previous_handlers()

    # Retrieve Shared Processors
    _shared_processors = _configure_shared_processors(json_logs=json_logs)

    # Configure Structlog
    # TODO: Review Logging First Use Cached Issue
    structlog.configure(
        processors=_shared_processors
        + [
            # Prepare event dict for `ProcessorFormatter`.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Define renderer
    _log_renderer: structlog.types.Processor
    if json_logs:
        _log_renderer = structlog.processors.JSONRenderer()
    else:
        _log_renderer = structlog.dev.ConsoleRenderer()

    # Define Formatter for StdLogging
    _formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within
        # structlog.
        foreign_pre_chain=_shared_processors,
        # These run on ALL entries after the pre_chain is done.
        processors=[
            # Remove _record & _from_structlog.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            _log_renderer,
        ],
    )

    # Handler for stdout output
    _handler_stdout = logging.StreamHandler(sys.stdout)
    _handler_stdout.setFormatter(_formatter)
    _handler_stdout.addFilter(StdoutFilter())

    # Handler for stderr output
    _handler_stderr = logging.StreamHandler(sys.stderr)
    _handler_stderr.setFormatter(_formatter)
    _handler_stderr.addFilter(StderrFilter())

    # Setup Root Handler
    root_logger = logging.getLogger()
    root_logger.addHandler(_handler_stdout)
    root_logger.addHandler(_handler_stderr)
    root_logger.setLevel(str(logging.getLevelName(log_level)).upper())
