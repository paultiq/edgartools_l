from pathlib import Path

from edgar import httpclient

# Base paths
FIXTURE_DIR = Path("tests/fixtures/xbrl2")
DATA_DIR = Path("data/xbrl/datafiles")

def pytest_addoption(parser):
    parser.addoption("--ratelimit_sqlite", action="store_true", help="Enable postgres ratelimiter, for multiprocessing")

def pytest_configure(config):
    """
    - Disables caching for testing
    - Confiugures a global rate limiter, which we need to ensure rate limits are respected

    """

    if config.getoption("--ratelimit_sqlite"):
        httpclient.update_rate_limiter(requests_per_second=httpclient._DEFAULT_REQUEST_PER_SEC_LIMIT, sqlite=True)
    else:
        raise ValueError("Unexpected")

    # Disable Cache for Tests
    httpclient.CACHE_DIRECTORY = None