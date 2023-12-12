from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from httpx import Response


class HttpRequestException(Exception):
    '''Thrown when an HTTP request does not fulfill the happy path.

    This exception should only be thrown if a response is successfully obtained
    after making the request; this is not intended for exceptions originating
    from the request itself (e.g. network timeout).
    '''
    response: 'Response'

    def __init__(self, response: 'Response', *args, **kwargs) -> 'None':
        self.response = response
        super().__init__(*args, **kwargs)
