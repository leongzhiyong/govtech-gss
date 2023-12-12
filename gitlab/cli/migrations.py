import alembic.config
import click
import os

from . import _options
from pathlib import Path


def _set_working_directory() -> 'None':
    '''Sets the working directory for Alembic to the project root.'''
    # slightly frail; may break if the directory structure is changed
    os.chdir(Path(__file__).resolve().parent.parent)


@click.command()
@_options.database_option()
def run(database: 'str') -> 'None':
    '''Executes database migrations.'''
    _set_working_directory()

    arguments = ('--raiseerr', '-x', f'database={database}', 'upgrade', 'head')
    alembic.config.main(argv=arguments)


@click.command()
@_options.database_option(ensure_exists=True)
def check(database: 'str') -> 'None':
    '''Executes database migration checks.'''
    _set_working_directory()

    arguments = ('-x', f'database={database}', 'check')
    alembic.config.main(argv=arguments)
