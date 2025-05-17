# myapp/consumers.py
import os, asyncio, logging
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
from test1.logging_handlers import WebSocketLogHandler

logger = logging.getLogger("file-tree")

class FileTreeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

        # 1. Attach our WebSocketLogHandler
        self.ws_handler = WebSocketLogHandler(self.send)
        # (optional) choose your log format
        self.ws_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(self.ws_handler)

        # 2. Kick off the scan in a thread
        asyncio.get_event_loop().run_in_executor(None, self._run_scan)

    def _run_scan(self):
        root_dir = settings.HISEQDATA_DIRECTORY
        for root, dirs, files in os.walk(root_dir):
            for filename in files:
                # now just log — the handler sends it to the browser
                logger.info(f"{root} ➔ {filename}")

        # final notice
        logger.info("--- Scan complete ---")

    async def disconnect(self, close_code):
        # Clean up: remove our handler so we don't leak connections
        logger.removeHandler(self.ws_handler)
