""" Provide all functions for logs processing """

import os

from opentelemetry import trace
from structlog.types import EventDict


def add_worker_pid(
    _, __, event_dict: EventDict  # pylint: disable=invalid-name
) -> EventDict:
    """Provide worker pid in the log to identify the instance"""
    event_dict["worker_pid"] = os.getpid()
    return event_dict


# https://github.com/hynek/structlog/issues/35#issuecomment-591321744
def rename_event_key(
    _, __, event_dict: EventDict  # pylint: disable=invalid-name
) -> EventDict:
    """
    Log entries keep the text message in the `event` field, but Datadog
    uses the `message` field. This processor moves the value from one field to
    the other.
    See https://github.com/hynek/structlog/issues/35#issuecomment-591321744
    """
    event_dict["message"] = event_dict.pop("event")
    return event_dict


def drop_color_message_key(
    _, __, event_dict: EventDict  # pylint: disable=invalid-name
) -> EventDict:
    """
    Uvicorn logs the message a second time in the extra `color_message`,
    but we don't need it. This processor drops the key from
    the event dict if it exists.
    """
    event_dict.pop("color_message", None)
    return event_dict


def add_open_telemetry_spans(_, __, event_dict):  # pylint: disable=invalid-name
    """Inject OpenTelemetry Span in the log event"""
    span = trace.get_current_span()
    if not span.is_recording():
        return event_dict

    ctx = span.get_span_context()
    parent = getattr(span, "parent", None)

    event_dict["span"] = {
        "span_id": hex(ctx.span_id),
        "trace_id": hex(ctx.trace_id),
        "parent_span_id": None if not parent else hex(parent.span_id),
    }

    return event_dict
