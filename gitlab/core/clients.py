import httpx

from .exceptions import HttpRequestException
from http import HTTPStatus
from json import JSONDecodeError
from typing import Any, Dict, Iterable, TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from .types import Domain, HttpStatusCode, MetadataDict, URL
    from httpx import Response


class GitLabClient:
    '''GitLab API wrapper with persistent httpx client instance.'''
    _client: 'httpx.Client'
    base_url: 'URL'

    def __init__(self, access_token: 'str', base_url: 'URL') -> 'None':
        self._client = httpx.Client(headers={ 'PRIVATE-TOKEN': access_token })
        self.base_url = base_url.rstrip('/')

    @property
    def domain(self) -> 'Domain':
        '''Returns the domain of the instance's base URL.'''
        netloc = urlparse(self.base_url).netloc
        # strip the credentials if present
        return netloc.split('@')[-1] if '@' in netloc else netloc

    def fetch_metadata(self) -> 'MetadataDict':
        '''Fetches the GitLab instance metadata.'''
        response = self._client.get(f'{self.base_url}/api/v4/metadata')

        self._ensure_http_status(response, (HTTPStatus.OK,))
        try:
            return response.json()
        except JSONDecodeError:
            raise HttpRequestException(response, 'Failed to decode response.')

    def health_check(self) -> 'str':
        '''Checks the health of the GitLab instance.'''
        response = self._client.get(f'{self.base_url}/-/health')
        self._ensure_http_status(response, (HTTPStatus.OK,))
        return response.text

    def readiness_check(self) -> 'Dict[str, Any]':
        '''Checks the readiness of the GitLab instance.'''
        response = self._client.get(f'{self.base_url}/-/readiness')

        self._ensure_http_status(response, (HTTPStatus.OK,))
        try:
            response_data = response.json()
        except JSONDecodeError:
            raise HttpRequestException(response, 'Failed to decode response.')
        else:
            if response_data.get('status').lower() != 'ok':
                raise HttpRequestException(response, 'Failed readiness check.')
            return response_data

    def _ensure_http_status(
        self,
        response: 'Response',
        allowed_codes: 'Iterable[HttpStatusCode]',
    ) -> 'None':
        '''Throws if the response status code is not one of the allowed codes.'''
        allowed_codes = set(map(int, allowed_codes))
        if response.status_code not in allowed_codes:
            message = (f'Expected one of HTTP {tuple(sorted(allowed_codes))}, '
                       f'got HTTP {response.status_code}')
            raise HttpRequestException(response, message)
