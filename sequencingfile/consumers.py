import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class LoggingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when the websocket is handshaking as part of connection.
        """
        await self.accept()
        # Start the logging task
        asyncio.create_task(self.send_logs())

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        print(f"WebSocket disconnected with code: {close_code}")
        # No specific cleanup needed here for this example

    async def receive(self, text_data=None, bytes_data=None):
        """
        Called when the server receives a message from the client.
        We are not expecting messages from the client in this example.
        """
        print(f"Received message from client (not used): {text_data}")
        # You can add logic here if you expect messages from the client

    async def send_logs(self):
        """
        Asynchronously sends a log message every second for 10 seconds.
        """
        for i in range(1, 11):
            try:
                # Send message to WebSocket
                await self.send(text_data=json.dumps({
                    'message': f'Log message: Second {i} of 10'
                }))
                print(f"Sent to client: Log message: Second {i} of 10")
                # Wait for 1 second
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Error sending log: {e}")
                # If an error occurs (e.g., client disconnected), break the loop
                break

        # Optionally, send a final message and close the connection
        try:
            await self.send(text_data=json.dumps({
                'message': 'Logging finished after 10 seconds.'
            }))
            print("Logging finished. Closing connection.")
            await self.close()
        except Exception as e:
            print(f"Error sending final message or closing: {e}")