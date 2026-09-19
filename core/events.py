"""Tiny event hook so tools/agent can report activity without printing raw to stdout."""

_handler = None


def set_handler(handler):
    global _handler
    _handler = handler


def get_handler():
    return _handler


def emit(message):
    if _handler is None:
        print(message)
    else:
        _handler(message)
