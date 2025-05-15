import json
from channels.generic.websocket import AsyncWebsocketConsumer

class JobNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f"user_{self.scope['user'].id}"

        if self.scope["user"].is_authenticated:
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        await self.send(text_data=json.dumps({"message": message}))

    async def send_job_notification(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))
#
# class JobNotificationConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.group_name = f"user_{self.scope['user'].id}"
#
#         if self.scope["user"].is_authenticated:
#             await self.channel_layer.group_add(self.group_name, self.channel_name)
#             await self.accept()
#         else:
#             await self.close()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.group_name, self.channel_name)
#
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']
#         await self.send(text_data=json.dumps({"message": message}))
#
#     async def send_job_notification(self, event):
#         await self.send(text_data=json.dumps({"message": event["message"]}))
