import pytest
from pathlib import Path
from typing import Dict, Any

from edgar.xbrl import XBRL
from edgar import httpclient

# Base paths
FIXTURE_DIR = Path("tests/fixtures/xbrl2")
DATA_DIR = Path("data/xbrl/datafiles")

def pytest_addoption(parser):
    parser.addoption("--ratelimit_postgres", action="store_true", help="Enable postgres ratelimiter, for multiprocessing")

def pytest_configure(config):
    """
    - Disables caching for testing

    To setup postgres:
    - docker run --name pg-limiter -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=ratelimit -p 5432:5432 -d postgres  -c max_connections=200
    - docker stop pg-limiter
    - docker rm -f pg-limiter

    """

    if config.getoption("--ratelimit_postgres"):
        from edgar.httpclient_ratelimiter import create_postgres_rate_limiter
        
        httpclient._RATE_LIMITER = create_postgres_rate_limiter(requests_per_second=10, max_delay=1000 * 60, postgres_url='postgresql://postgres:pass@localhost:5432/ratelimit')
    else:
        raise ValueError("Unexpected")
    
    # Disable Cache
    httpclient.CACHE_DIRECTORY = None