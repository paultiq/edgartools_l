import logging
import httpx
from httpx_ratelimiter import LimiterTransport, AsyncLimiterTransport

log = logging.getLogger(__name__)

MAX_REQUESTS_PER_SECOND = 10

_LIMITER = None

def transport_factory() -> httpx.HTTPTransport:
    log.debug("Creating LimiterTransport")
    global _LIMITER
    if _LIMITER is None:
        transport = LimiterTransport(per_second=MAX_REQUESTS_PER_SECOND, max_delay=5000)
        _LIMITER = transport.limiter
    else:
        return LimiterTransport(per_second=MAX_REQUESTS_PER_SECOND, max_delay=5000, limiter=_LIMITER)
    
    return transport

def async_transport_factory() -> httpx.AsyncBaseTransport:
    if _LIMITER is None:
        transport_factory()
        
    log.debug("Creating AsyncLimiterTransport")

    return AsyncLimiterTransport(per_second=MAX_REQUESTS_PER_SECOND, max_delay=5000, limiter = _LIMITER)