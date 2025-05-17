# myapp/consumers.py
import re
import os, asyncio, logging
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test1.settings")
django.setup()

from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
from test1.logging_handlers import WebSocketLogHandler
from sequencingfile.models import SequencingFile, SequencingFileSet
from sequencingrun.models import SequencingRun
from sequencinglib.models import SequencingLib

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
        pattern = re.compile(r"\.(?:bam|bai|fastq\.gz)$", re.IGNORECASE)

        for root, dirs, files in os.walk(root_dir):
            for filename in files:
                if pattern.search(filename):
                    # Log path and filename
                    logger.info(f"{root} ➔ {filename}")

        # final notice
        logger.info("--- Scan complete ---")

    async def disconnect(self, close_code):
        # Clean up: remove our handler so we don't leak connections
        logger.removeHandler(self.ws_handler)
