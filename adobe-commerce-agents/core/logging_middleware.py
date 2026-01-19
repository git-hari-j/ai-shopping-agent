from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from config import settings
import logging
import time
import json

logger = logging.getLogger("api_logger")
logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
if not logger.handlers:
    logger.addHandler(handler)

class DetailedLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.DEBUG:
            return await call_next(request)

        # Log Request
        start_time = time.time()
        body = await request.body()
        logger.info(f"Incoming Request: {request.method} {request.url}")
        logger.debug(f"Headers: {dict(request.headers)}")
        if body:
            try:
                # Try to pretty print JSON
                logger.debug(f"Body: {json.dumps(json.loads(body), indent=2)}")
            except:
                logger.debug(f"Body: {body.decode('utf-8', errors='ignore')}")

        # Process Request
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log Response
        logger.info(f"Response Status: {response.status_code} (Time: {process_time:.4f}s)")

        # Note: We cannot easily read response body here without consuming the stream,
        # which breaks the response for the client unless we reconstruct it.
        # For simplicity/performance, we log status and time.
        # If deeply needed, we can wrap the response iterator.

        return response
