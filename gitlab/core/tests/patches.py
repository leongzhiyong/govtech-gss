from httpx import Response
from contextlib import contextmanager
from typing import Any, Dict, Iterator, TYPE_CHECKING
from unittest import mock

if TYPE_CHECKING:
    from httpx import Client


@contextmanager
def patched_client_context(
    client: 'Client',
    method: 'str',
    code: 'int',
    *,
    text_body: 'str' = None,
    json_body: 'Dict[str, Any]' = None,
) -> 'Iterator[Client]':
    '''Patches the specified HTTPX client method with the given response code and body.'''
    with mock.patch.object(client, method) as patched_method:
        # patch the method to return a proper `Response`
        patched_method.return_value = Response(code, text=text_body, json=json_body)
        yield patched_method
