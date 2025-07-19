import pytest
from pathlib import Path
from typing import Dict, Any

from edgar.xbrl import XBRL
from edgar import httpclient
from edgar.httpclient_ratelimiter import create_postgres_rate_limiter, create_sqlite_rate_limiter

# Base paths
FIXTURE_DIR = Path("tests/fixtures/xbrl2")
DATA_DIR = Path("data/xbrl/datafiles")

def pytest_addoption(parser):
    parser.addoption("--ratelimit_postgres", action="store_true", help="Enable postgres ratelimiter, for multiprocessing")
    parser.addoption("--ratelimit_sqlite", action="store_true", help="Enable postgres ratelimiter, for multiprocessing")

def pytest_configure(config):
    """
    - Disables caching for testing
    - Confiugures a global rate limiter, which we need to ensure rate limits are respected

    """

    if config.getoption("--ratelimit_postgres"):
        """    
        To setup postgres for testing
        - docker run --name pg-limiter -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=ratelimit -p 5432:5432 -d postgres  -c max_connections=200
        - docker stop pg-limiter
        - docker rm -f pg-limiter
        """
        httpclient._RATE_LIMITER = create_postgres_rate_limiter(requests_per_second=10, max_delay=1000 * 60, postgres_url='postgresql://postgres:pass@localhost:5432/ratelimit')
    
    if config.getoption("--ratelimit_sqlite"):
        httpclient._RATE_LIMITER = create_sqlite_rate_limiter(requests_per_second=10, max_delay=1000 * 60)


    # Disable Cache
    httpclient.CACHE_DIRECTORY = None