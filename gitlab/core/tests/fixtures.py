import pytest
import uuid

from .. import GitLabClient


@pytest.fixture
def access_token() -> 'str':
    '''UUID string as an access token.'''
    yield str(uuid.uuid4())

@pytest.fixture
def client(access_token: 'str', instance_url: 'str') -> 'GitLabClient':
    '''GitLab client.'''
    yield GitLabClient(access_token, instance_url)

@pytest.fixture
def instance_url() -> 'str':
    '''GitLab instance URL.'''
    yield 'https://example.com'
