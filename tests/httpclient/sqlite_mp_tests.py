from edgar import httpclient_ratelimiter
import edgar
from edgar import httpclient, Company
from concurrent.futures import ProcessPoolExecutor

import logging

logger = logging.getLogger(__name__)

def init_sqlrate_limiter():
    """Each process in the processpool must be initialized with a new rate limiter"""
    httpclient._RATE_LIMITER = httpclient_ratelimiter.create_sqlite_rate_limiter(10, 60000)

def get_company_filings(company): 
    try:
        logger.info(f"Getting {company}")
        
        filings = Company(company).get_filings(form="10-Q")
        return filings
    except Exception as e:
        logger.exception(f"Unable to get filing for {company}")
        raise e
        
def test_mp():
    companies = ["IBM", "MSFT", "TSLA", "UPS"]

    with ProcessPoolExecutor(initializer = init_sqlrate_limiter) as executor:
        results = list(executor.map(get_company_filings, companies))

    assert len(results) == 4
    assert isinstance(results[0][0], edgar.entity.filings.EntityFiling)
        

if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
        level=logging.DEBUG,
        datefmt='%Y-%m-%d %H:%M:%S')

    test_mp()