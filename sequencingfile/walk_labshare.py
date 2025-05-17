import os, asyncio, json
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

class FileTreeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # kick off the blocking scan in a thread
        asyncio.get_event_loop().run_in_executor(None, async_to_sync(self._run_scan))

    def _run_scan(self):
        """
        Runs in a thread so we don’t block the event loop.
        Uses async_to_sync(self.send) to push into the WebSocket.
        """
        for root_dir in settings.HISEQDATA_DIRECTORY:
            for root, dirs, files in os.walk(root_dir):
                rel = root.replace(settings.HISEQDATA_DIRECTORY, "")
                for fn in files:
                    message = f"{rel} ➔ {fn}"
                    # send via the open socket
                    async_to_sync(self.send)(
                        text_data=json.dumps({"message": message})
                    )
        # optional: let client know we're done
        async_to_sync(self.send)(
            text_data=json.dumps({"complete": True})
        )

    async def disconnect(self, close_code):
        # nothing special to clean up in this simple example
        pass
