from base_logger import get_logger
from logging import Logger
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from typing import Tuple, List
import json

logger: Logger = get_logger(__name__)


def paginated_request(method: str, url: str, headers: dict = None, body=None) -> List:
    """
    Simple paginated request implementation.

    :param method: Request type. EXamples: GET, POST...
    :param url: URL to request
    :param headers: [Optional] Request headers
    :param body: [Optional] Request body
    :return: A collection of paginated requests converted to List
    """

    has_more_objects = True
    page_size = 1000
    page = 1
    responses: List = []

    while has_more_objects:
        page_url = f"{url}?page={page}&page_size={page_size}"
        logger.debug(f"Starting {method} request for {page_url}")
        req = Request(page_url, data=body, headers=headers, method=method)
        try:
            # Request URL, checking request, convert response to json.
            with urlopen(req) as open_request:
                status = open_request.status
                response = open_request.read()
                if response_is_ok(status, page_url):
                    data = json.loads(response)
                    if data:
                        responses.extend(data)
                        page += 1
                    else:
                        has_more_objects = False
                else:
                    # Looks like something goes wrong with endpoint, canceling requests queue.
                    has_more_objects = False
        except HTTPError as e:
            logger.error(f"Cannot request {page_url} with {method} method, error: {e.code} {str(e)}")
            return e.code, str(e).encode()

    return responses


def response_is_ok(status: int, url: str):
    if status != 200:
        logger.info(f"Failed to perform request of {url}, status is {status}")
        return False
    else:
        logger.debug(f"Successfully performed request of {url}, status is {status}")
        return True

def get(*args, **kwargs):
    return paginated_request("GET", *args, **kwargs)

