import logging
from datetime import datetime, timedelta

from app.exceptions import TooManyRequestsException
from fastapi import Request

# In-memory store for rate limiting (could be more complex, depending on requirements)
rate_limit_store = {}

# Settings
RATE_LIMIT = 10
TIME_WINDOW = timedelta(minutes=1)

logger = logging.getLogger(__name__)


# Custom dependency to limit rate
async def rate_limiter(request: Request):
    client_ip = request.client.host
    now = datetime.utcnow()

    # Get the list of request times for the client IP
    if client_ip in rate_limit_store:
        request_times = rate_limit_store[client_ip]
    else:
        request_times = []

    # Filter out requests outside the time window
    request_times = [time for time in request_times if now - time < TIME_WINDOW]

    # Check if the client has exceeded the rate limit
    if len(request_times) >= RATE_LIMIT:
        raise TooManyRequestsException("Too many requests")

    # Add the current time to the list of request times
    request_times.append(now)
    rate_limit_store[client_ip] = request_times


async def clear_rate_limit_store():
    logger.info("Clearing rate limit store")
    now = datetime.utcnow()
    for ip, times in list(rate_limit_store.items()):
        # Remove old request times
        rate_limit_store[ip] = [t for t in times if now - t < TIME_WINDOW]
        # Remove IP if no recent requests
        if not rate_limit_store[ip]:
            del rate_limit_store[ip]
