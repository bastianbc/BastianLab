
# yourapp/views.py

import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class LogStreamerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("connection is open")
        # launch background task to push logs
        self.log_task = asyncio.create_task(self.stream_logs())

    async def disconnect(self, close_code):
        print("connection is closed")
        # clean up when client disconnects
        self.log_task.cancel()

    async def stream_logs(self):
        """
        Replace this loop with reading your real log source.
        For example, tailing a file or subscribing to an external logger.
        """
        counter = 1
        try:
            print(f"stream logs {counter}")
            while True:
                message = f"[{counter}] Example log entry"
                await self.send(text_data=message)
                counter += 1
                await asyncio.sleep(1)   # simulate delay
        except asyncio.CancelledError:
            pass  # task was cancelled on disconnect

    async def receive(self, text_data):
        # (Optional) handle messages from the client here
        pass
