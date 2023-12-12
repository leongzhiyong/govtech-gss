import click
import csv
import json
import sqlalchemy
import sqlalchemy.orm
import time
import traceback

from . import _options
from contextlib import contextmanager
from datetime import datetime
from gitlab.core import GitLabClient, HttpRequestException, PollEntry
from pathlib import Path


def _poll_once(database: 'str', access_token: 'str', instance: 'str', save_responses: 'bool') -> 'None':
    '''Polls the specified GitLab instance once.'''
    client = GitLabClient(access_token, instance)
    poll_entry = PollEntry(
        base_url=instance,
        health_check_passed=False,
        instance_version='',
        readiness_check_passed=False,
    )

    click.echo(f'[ {datetime.now().isoformat()} ] Polling GitLab instance at {client.domain}...', err=True)
    try:
        click.echo(f'  Performing health check...', err=True)
        with _possible_http_exception_context(f'    Failed: {{body}}'):
            health_check_output = client.health_check()
            poll_entry.health_check_passed = True
            if save_responses:
                poll_entry.health_check_response = health_check_output
            click.echo(f'    Passed: {repr(health_check_output)}', err=True)

        click.echo(f'  Performing readiness check...', err=True)
        with _possible_http_exception_context(f'    Failed: {{body}}'):
            readiness_check_output = client.readiness_check()
            readiness_check_output_encoded = json.dumps(readiness_check_output)
            poll_entry.readiness_check_passed = True
            if save_responses:
                poll_entry.readiness_check_response = readiness_check_output_encoded
            click.echo(f'    Passed: {readiness_check_output_encoded}', err=True)

        click.echo(f'  Fetching metadata...', err=True)
        with _possible_http_exception_context(f'    Failed: {{body}}'):
            metadata = client.fetch_metadata()
            metadata_encoded = json.dumps(metadata)
            poll_entry.instance_version = metadata['version']
            if save_responses:
                poll_entry.metadata_response = json.dumps(metadata)
            click.echo(f'    Passed: {metadata_encoded}', err=True)
    except Exception as exception:
        poll_entry.error_message = ''.join(traceback.format_exception(exception)).strip()
        click.echo(f'  Critical failure: {str(exception)}', err=True)
    finally:
        engine = sqlalchemy.create_engine(database)
        with sqlalchemy.orm.Session(engine) as session:
            session.add(poll_entry)
            session.commit()


@contextmanager
def _possible_http_exception_context(error_template: 'str') -> 'None':
    '''Provides a context that handles and suppreses `HttpRequestException`.

    `error_template` will be interpolated with the keyworded argument "body"
    using the response body.
    '''
    try:
        yield
    except HttpRequestException as exception:
        message = error_template.format(body=exception.response.text)
        click.echo(message, err=True)


def _validate_access_token(_ctx, _param, value: 'str') -> 'str':
    '''Handles a known bug with pasting from clipboard on the Windows Command Prompt terminal.

    See https://bugs.python.org/issue37426.
    '''
    if value == '\x16': # ctrl+V is read as the SYN 0x16 character
        warning = (
            '''Unable to read pasted input; this is a known issue with some terminals (e.g. Command Prompt).\n'''
            '''You may opt for one of the following alternatives:\n'''
            '''  1. Look for a way to paste without using the CTRL+V keyboard shortcut.\n'''
            '''     This may possibly be a right-click on the mouse, or a menu option.\n'''
            '''  2. Provide the access token as the `GITLAB_ACCESS_TOKEN` environment variable.\n'''
            '''  3. Provide the access token using the --token command line option.\n'''
            '''See https://bugs.python.org/issue37426 for more information.'''
        )
        click.secho(click.style(warning, fg='bright_yellow'), err=True)
        raise click.UsageError('Invalid password input.')
    return value


@click.command()
@click.option(
    '-u', '--url', 'instance',
    help='GitLab instance URL',
    required=True,
)
@click.password_option(
    '-t', '--token', 'access_token',
    callback=_validate_access_token,
    confirmation_prompt=False,
    envvar='GITLAB_ACCESS_TOKEN',
    help='GitLab access token.',
    prompt='GitLab access token',
    required=True,
    show_envvar=True,
)
@_options.database_option(ensure_exists=True)
@click.option(
    '-c', '--continuous', 'run_continuously',
    help='Run countinuously.',
    is_flag=True,
)
@click.option(
    '-t', '--interval', 'poll_interval',
    default=300.0,
    help='Polling interval (seconds); only applies with the --continuous flag.',
    show_default=True,
    type=float,
)
@click.option(
    '--save-responses', 'save_responses',
    help='Persist response information to database.',
    is_flag=True,
)
def poll(
    database: 'str',
    access_token: 'str',
    instance: 'str',
    run_continuously: 'bool',
    poll_interval: 'float',
    save_responses: 'bool',
) -> 'None':
    '''Polls the specified GitLab instance.'''
    if run_continuously:
        click.echo(f'Polling continuously with an interval of {poll_interval:.2f}s...', err=True)

        while True:
            try:
                click.echo(err=True)
                _poll_once(database, access_token, instance, save_responses)
                time.sleep(poll_interval)
            except KeyboardInterrupt:
                click.echo('Interrupt received. Stopping...', err=True)
                break
    else:
        _poll_once(database, access_token, instance, save_responses)


@click.command()
@click.option(
    '-o', '--output', 'output',
    help='Export path.',
    required=True,
    type=click.Path(
        dir_okay=False,
        path_type=Path,
        readable=True,
        writable=True,
    ),
)
@_options.database_option(ensure_exists=True)
@click.option(
    '-u', '--url', 'filter_instance',
    help='GitLab instance URL to filter.',
)
@click.option(
    '-f', '--from', 'filter_from',
    help='Filter from timestamp (inclusive).',
    type=click.DateTime(formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']),
)
@click.option(
    '-t', '--to', 'filter_to',
    help='Filter to timestamp (exclusive).',
    type=click.DateTime(formats=['%Y-%m-%d', '%Y-%m-%d %H:%M:%S']),
)
@click.option(
    '--include-responses', 'include_responses',
    help='Include response information in the export.',
    is_flag=True,
)
def export(
    output: 'Path',
    database: 'str',
    include_responses: 'bool',
    filter_instance: 'str | None',
    filter_from: 'datetime | None',
    filter_to: 'datetime | None',
) -> 'None':
    '''Export poll records from the specified GitLab instance.'''
    if output.exists(): # prevent overwriting files
        raise click.ClickException(f'File already exists: {output.as_posix()}')

    if any((filter_instance, filter_from, filter_to)):
        click.echo(f'Applying filters to exported queryset...', err=True)
        click.echo(f'  instance url:   {filter_instance}', err=True)
        click.echo(f'  from timestamp: {"<none>" if filter_from is None else filter_from.isoformat()}', err=True)
        click.echo(f'  to timestamp:   {"<none>" if filter_to is None else filter_to.isoformat()}', err=True)
    else:
        click.echo('No filters specified. Entire database will be exported...', err=True)

    engine = sqlalchemy.create_engine(database)
    stmt = sqlalchemy.select(PollEntry).order_by(PollEntry.created_at)

    # apply filters if they have been provided
    if filter_instance is not None:
        stmt = stmt.where(PollEntry.base_url == filter_instance)
    if filter_from is not None:
        stmt = stmt.where(PollEntry.created_at >= filter_from)
    if filter_to is not None:
        stmt = stmt.where(PollEntry.created_at < filter_to)

    # create a mapping of fields to their transformers
    return_self = lambda x: x
    fields = {
        'base_url': return_self,
        'instance_version': return_self,
        'health_check_passed': lambda x: 'yes' if x else 'no',
        'readiness_check_passed': lambda x: 'yes' if x else 'no',
        'created_at': lambda x: x.strftime('%Y-%m-%d %H:%M:%S'),
    }
    if include_responses:
        fields.update({
            'health_check_response': return_self,
            'readiness_check_response': return_self,
            'metadata_response': return_self,
        })

    # execute the query for export
    click.echo('Beginning export...', err=True)
    with output.open('w', encoding='utf-8') as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_ALL)
        writer.writerow(fields)
        with sqlalchemy.orm.Session(engine) as session:
            for i, entry in enumerate(session.execute(stmt).scalars(), 1):
                writer.writerow([getattr(entry, field) for field in fields])
            click.echo(f'Completed export of {i} rows', err=True)
