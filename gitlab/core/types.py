from typing import Any, Dict, NewType, TypedDict


Domain = NewType('Domain', str)
HttpStatusCode = NewType('HttpStatusCode', int)
URI = NewType('URI', str)
URL = NewType('URL', URI)


class KubernetesDict(TypedDict):
    '''Represents the GitLab KAS metadata object.'''
    enabled: 'bool'
    externalUrl: 'URI | None'
    version: 'str | None'


class MetadataDict(TypedDict):
    '''Represents the GitLab instance metadata object.

    See https://docs.gitlab.com/ee/api/metadata.html.
    '''
    enterprise: 'bool'
    kas: 'Dict[str, Any]'
    revision: 'str'
    version: 'str'
