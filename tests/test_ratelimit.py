from edgar.httpclient import async_http_client, http_client

import pytest
import time
import asyncio

def test_cache_speedup(request):
    """Verify that 30 requests take more than 3 seconds (given a rate limit of 9-10 requests per second), and
    all return status_code 200"""


    cacheable_url = 'https://www.sec.gov/Archives/edgar/data/730200/000073020016000084/0000730200-16-000084.txt'

    count = 30

    start = time.perf_counter()
    with http_client() as client:
        for _ in range(count):
            response = client.get(cacheable_url)
            assert response.status_code == 200

    end = time.perf_counter()

    duration = end - start
    cache_enabled = request.config.getoption("--enable-cache")
    if cache_enabled:
        assert duration > 3.0 and duration < 5.0, f"{duration=} not between 3 and 5 seconds"
    else:
        assert duration < 1, f"With cache enabled, {duration=} is longer than a second"
        
def test_dont_exceed_limit():
    """Verify that 30 requests take more than 3 seconds (given a rate limit of 9-10 requests per second), and
    all return status_code 200"""
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"
    count = 30

    start = time.perf_counter()
    with http_client() as client:
        for _ in range(count):
            response = client.get(url)
            assert response.status_code == 200

    end = time.perf_counter()

    duration = end - start
    assert duration > 3.0 and duration < 5.0, f"{duration=} not between 3 and 5 seconds"

@pytest.mark.asyncio
async def test_dont_exceed_limit_async():
    """Verify that 30 requests take more than 3 seconds (given a rate limit of 9-10 requests per second), and
    all return status_code 200"""
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent"
    count = 30

    start = time.perf_counter()
    async with async_http_client() as client:
        tasks = [client.get(url) for _ in range(count)]
        results = await asyncio.gather(*tasks)
        for r in results:
            assert r.status_code == 200
    end = time.perf_counter()

    duration = end - start
    assert duration > 3.0, f"{duration=} was faster than available rate limit"