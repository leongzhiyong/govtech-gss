from .fixtures import * # import to initialise fixtures

import re

from .. import HttpRequestException
from .patches import patched_client_context
from http import HTTPStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .. import GitLabClient


def test_health_check(client: 'GitLabClient') -> 'None':
    '''Health check.'''
    code, body = HTTPStatus.OK, 'GitLab OK'
    with patched_client_context(client._client, 'get', code, text_body=body):
        retval = client.health_check()
        assert retval == body


def test_health_check_with_invalid_endpoint(client: 'GitLabClient') -> 'None':
    '''Health check against an invalid endpoint.'''
    with pytest.raises(
        HttpRequestException,
        match=re.compile(r'expected one of http \(200,\)', re.IGNORECASE),
    ):
        client.health_check()


def test_readiness_check(client: 'GitLabClient') -> 'None':
    '''Readiness check.'''
    code, body = HTTPStatus.OK, {'status': 'ok', 'master_check': [{'status': 'ok'}]}
    with patched_client_context(client._client, 'get', code, json_body=body):
        retval = client.readiness_check()
        assert retval == body


def test_readiness_check_with_invalid_endpoint(client: 'GitLabClient') -> 'None':
    '''Readiness check against an invalid endpoint.'''
    with pytest.raises(
        HttpRequestException,
        match=re.compile(r'expected one of http \(200,\)', re.IGNORECASE),
    ):
        client.readiness_check()


def test_unparseable_readiness_check_response(client: 'GitLabClient') -> 'None':
    '''Readiness check with unparseable response body.'''
    code, body = HTTPStatus.OK, 'not valid json'
    with patched_client_context(client._client, 'get', code, text_body=body):
        with pytest.raises(
            HttpRequestException,
            match=re.compile(r'failed to decode response', re.IGNORECASE),
        ):
            client.readiness_check()


def test_failing_readiness_check(client: 'GitLabClient') -> 'None':
    '''Readiness check with a failing status value.'''
    code, body = HTTPStatus.OK, {'status': 'failed', 'master_check': [{'status': 'ok'}]}
    with patched_client_context(client._client, 'get', code, json_body=body):
        with pytest.raises(
            HttpRequestException,
            match=re.compile(r'failed readiness check', re.IGNORECASE),
        ):
            client.readiness_check()


def test_fetch_metadata(client: 'GitLabClient') -> 'None':
    '''Fetch instance metadata.'''
    code = HTTPStatus.OK
    body = {
        'version': '16.6.1-ee',
        'revision': '9aa991a5ee9',
        'kas': {
            'enabled': True,
            'externalUrl': 'ws://localhost:/-/kubernetes-agent/',
            'version': 'v16.6.0',
        },
        'enterprise': True,
    }
    with patched_client_context(client._client, 'get', code, json_body=body):
        retval = client.fetch_metadata()
        assert retval == body


def test_fetch_metadata_with_invalid_endpoint(client: 'GitLabClient') -> 'None':
    '''Fetch instance metadata from an invalid endpoint.'''
    with pytest.raises(
        HttpRequestException,
        match=re.compile(r'expected one of http \(200,\)', re.IGNORECASE),
    ):
        client.fetch_metadata()


def test_unparseable_fetch_metadata_response(client: 'GitLabClient') -> 'None':
    '''Fetch instance metadata with unparseable response body.'''
    code, body = HTTPStatus.OK, 'not valid json'
    with patched_client_context(client._client, 'get', code, text_body=body):
        with pytest.raises(
            HttpRequestException,
            match=re.compile(r'failed to decode response', re.IGNORECASE),
        ):
            client.fetch_metadata()


def test_unauthorised_fetch_metadata_response(client: 'GitLabClient') -> 'None':
    '''Fetch instance metadata without sufficient authorisation.'''
    code, body = HTTPStatus.UNAUTHORIZED, { 'error': 'insufficient_scope' }
    with patched_client_context(client._client, 'get', code, json_body=body):
        with pytest.raises(
            HttpRequestException,
            match=re.compile(r'expected one of http \(200,\)', re.IGNORECASE),
        ):
            client.fetch_metadata()
