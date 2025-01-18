# Copyright (C) 2024, IQMO Corporation [support@iqmo.com]
# All Rights Reserved
# Setup Client
from edgar import core
import logging
import hishel
from httpx_ratelimiter import LimiterTransport
import httpcore
from typing import Optional, Union
import httpx
from edgar.http.httpclient_ratelimiter import transport_factory, async_transport_factory

from httpcore import Request, Response
from hishel import Controller
from functools import partial
from edgar.http import httpclient
from pathlib import Path

log = logging.getLogger(__name__)

class ForceCacheController(Controller):
    def is_cachable(self, request: Request, response: Response) -> bool:
        print("request is cachable", request.url)
        return True

    def construct_response_from_cache(
        self, request: Request, response: Response, original_request: Request
    ) -> Optional[Union[Response, Request]]:
        # Only do not use the cache if the vary headers does not match
        # This would prevent the cache to use a response that was meant for another request
        # For example, if the original request had the header "Accept: application/json"
        # but the current request has "Accept: text/html", the cache should not be used
        if not self._validate_vary(
            request=request, response=response, original_request=original_request
        ):
            log.info("Can't use cache", request)
            return None

        log.info("Using cached response")
        return response

def custom_key_generator(request: httpcore.Request, body: bytes):
    host = request.url.host.decode()
    url = request.url.target.decode()

    url_p = url.replace("/", "__")

    key = f"{host}_{url_p}"
    log.info(f"{key}")
    return key

controller = ForceCacheController(
        # Cache only GET and POST methods
        cacheable_methods=["GET", "POST"],
        # Cache only 200 status codes
        cacheable_status_codes=[200],
        # Use the stale response if there is a connection issue and the new response cannot be obtained.
        allow_stale=True,
        # First, revalidate the response and then utilize it.
        # If the response has not changed, do not download the
        # entire response data from the server; instead,
        # use the one you have because you know it has not been modified.
        always_revalidate=False,
        key_generator=custom_key_generator,
    )

storage = hishel.FileStorage(base_path=Path("c:/git/hishel_cache"))

def install_cached_client():
    httpclient._CLIENT_IMPL =  hishel.CacheClient
    httpclient._ASYNC_CLIENT_IMPL = hishel.AsyncCacheClient
    httpclient.DEFAULT_PARAMS["controller"] = controller
    httpclient.DEFAULT_PARAMS["storage"] = storage
