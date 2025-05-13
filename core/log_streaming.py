# log_streaming/middleware.py
import asyncio
import logging
import threading
import time
import uuid
from asgiref.sync import sync_to_async
from collections import deque
from django.conf import settings
from typing import Dict, Deque, Optional

# Global log buffer to store logs per request
_request_logs: Dict[str, Deque[str]] = {}
# Lock for thread safety when accessing the log buffer
_buffer_lock = threading.Lock()


class AsyncLogStreamHandler(logging.Handler):
    """Custom logging handler that stores logs in a request-specific buffer."""

    def __init__(self):
        super().__init__()
        self.setLevel(logging.DEBUG)
        self.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))

    def emit(self, record):
        try:
            request_id = getattr(threading.current_thread(), 'request_id', None)
            if request_id:
                log_message = self.format(record)
                with _buffer_lock:
                    if request_id in _request_logs:
                        _request_logs[request_id].append(log_message)
        except Exception:
            self.handleError(record)


class AsyncLogStreamMiddleware:
    """
    Middleware that initializes a request-specific log buffer and provides
    methods to stream logs asynchronously.
    """

    def __init__(self, get_response):
        self.get_response = get_response

        # Install the custom log handler if not already installed
        self._install_log_handler()

    def _install_log_handler(self):
        """Install our custom log handler to the root logger if not already present."""
        root_logger = logging.getLogger()

        # Check if our handler is already installed
        for handler in root_logger.handlers:
            if isinstance(handler, AsyncLogStreamHandler):
                return

        # Add our handler to the root logger
        handler = AsyncLogStreamHandler()
        root_logger.addHandler(handler)

    async def __call__(self, scope, receive, send):
        """ASGI application entry point."""
        if scope["type"] != "http":
            # Pass through non-HTTP requests directly
            await self.get_response(scope, receive, send)
            return

        # Generate a unique ID for this request
        request_id = str(uuid.uuid4())

        # Set the request ID on the current thread
        threading.current_thread().request_id = request_id

        # Initialize the log buffer for this request
        with _buffer_lock:
            _request_logs[request_id] = deque(maxlen=getattr(settings, 'LOG_BUFFER_MAX_SIZE', 1000))

        # Add the request_id to the scope for later access in views
        scope['log_request_id'] = request_id

        # Process the request and get response
        try:
            await self.get_response(scope, receive, send)
        finally:
            # Clean up log buffer after response is sent
            with _buffer_lock:
                if request_id in _request_logs:
                    del _request_logs[request_id]

            # Clean up thread local
            try:
                delattr(threading.current_thread(), 'request_id')
            except AttributeError:
                pass


class LogStreamer:
    """
    Utility class to assist with streaming logs for a specific request.
    Can be used in an async view to stream logs to the client.
    """

    def __init__(self, request_id: str):
        self.request_id = request_id
        self.last_position = 0

    async def get_new_logs(self) -> list:
        """Get new log entries since the last check."""

        @sync_to_async
        def _get_logs():
            with _buffer_lock:
                if self.request_id not in _request_logs:
                    return []

                logs = list(_request_logs[self.request_id])
                new_logs = logs[self.last_position:]
                self.last_position = len(logs)
                return new_logs

        return await _get_logs()

    async def stream(self, timeout=60, interval=0.5):
        """
        Generator that yields new log entries as they arrive.

        Args:
            timeout: Maximum time in seconds to stream logs
            interval: Time in seconds between log checks
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            new_logs = await self.get_new_logs()

            if new_logs:
                for log in new_logs:
                    yield log

            await asyncio.sleep(interval)


def get_log_streamer(request_or_scope) -> Optional[LogStreamer]:
    """
    Helper function to get a LogStreamer instance for a request.

    Args:
        request_or_scope: Django Request object or ASGI scope

    Returns:
        LogStreamer instance or None if request ID not found
    """
    if hasattr(request_or_scope, 'log_request_id'):
        # Django request object
        request_id = request_or_scope.log_request_id
    elif isinstance(request_or_scope, dict) and 'log_request_id' in request_or_scope:
        # ASGI scope
        request_id = request_or_scope['log_request_id']
    else:
        return None

    return LogStreamer(request_id)