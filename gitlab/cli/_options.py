import click

from pathlib import Path
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from click.decorators import FC


def database_option(
    name: 'str' = 'database',
    *,
    ensure_exists: 'bool' = False,
    as_sqlite_uri: 'bool' = True,
) -> 'Callable[[FC], FC]':
    '''Generate a `click` option decorator for a database file.'''
    def sqllite_uri(_ctx, _parameter, path: 'Path') -> 'str':
        return f'sqlite:///{path.as_posix()}'

    return click.option(
        '-d', '--database', name,
        callback=sqllite_uri if as_sqlite_uri else None,
        help='Path to the sqlite database file.',
        required=True,
        type=click.Path(
            dir_okay=False,
            exists=ensure_exists,
            path_type=Path,
            readable=True,
            resolve_path=True,
            writable=True,
        ),
    )
