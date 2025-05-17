# myapp/consumers.py
import os, asyncio, json, logging
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger("file-tree")

class FileTreeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Log on server
        logger.debug("WebSocket CONNECTED from %s", self.scope["client"])
        await self.accept()
        # Send an initial handshake message
        await self.send(json.dumps({"message": "🟢 Connection accepted, starting scan…"}))
        # Offload your blocking scan
        asyncio.get_event_loop().run_in_executor(None, self._run_scan)

    def _run_scan(self):
        for root_dir in [settings.HISEQDATA_DIRECTORY]:
            for root, dirs, files in os.walk(root_dir):
                rel = root.replace(root_dir, "")
                for fn in files:
                    payload = {"message": f"{rel} ➔ {fn}"}
                    async_to_sync(self.send)(text_data=json.dumps(payload))
        # final “done” message
        async_to_sync(self.send)(text_data=json.dumps({"complete": True}))

    async def disconnect(self, close_code):
        logger.debug("WebSocket DISCONNECTED (code=%s)", close_code)
