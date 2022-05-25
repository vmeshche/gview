from base_logger import get_logger
from logging import Logger
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from typing import Tuple

logger: Logger = get_logger(__name__)


def request(method: str, url: str, headers: dict = None, body=None) -> Tuple[int, bytes]:
    logger.debug(f"Starting {method} request for {url}")
    req = Request(url, data=body, headers=headers, method=method)

    try:
        with urlopen(req) as open_request:
            status = open_request.status
            response = open_request.read()
    except HTTPError as e:
        logger.error(f"Cannot request {url} with {method} method, error: {e.code} {str(e)}")
        return e.code, str(e).encode()

    return status, response


def get(*args, **kwargs):
    return request("GET", *args, **kwargs)