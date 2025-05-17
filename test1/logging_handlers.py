# somewhere in your project, e.g. test1/logging_handlers.py
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class WebsocketLogHandler(logging.Handler):
    def emit(self, record):
        try:
            message = self.format(record)
            channel_layer = get_channel_layer()
            # send to the “logging” group
            async_to_sync(channel_layer.group_send)(
                "logging",
                {
                    "type": "log_message",   # maps to the method name in consumer
                    "message": message,
                }
            )
        except Exception:
            # don’t let logging failures crash your app
            self.handleError(record)
