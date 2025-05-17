# myapp/log_handlers.py
import logging
from asgiref.sync import async_to_sync

class WebSocketLogHandler(logging.Handler):
    """
    A logging.Handler that routes every log record
    straight into a WebSocket.send(text_data=...).
    """
    def __init__(self, send_method):
        super().__init__()
        self.send_method = send_method

    def emit(self, record):
        try:
            msg = self.format(record)
            # send raw text over the open WebSocket
            async_to_sync(self.send_method)(text_data=msg)
        except Exception:
            self.handleError(record)
