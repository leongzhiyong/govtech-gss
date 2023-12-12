import click

from gitlab.cli import migrations, polls


@click.group()
def cli() -> 'None':
    pass


# add commands here
cli.add_command(migrations.run, 'migrate')
cli.add_command(migrations.check, 'check_migrations')
cli.add_command(polls.poll, 'poll')
cli.add_command(polls.export, 'export')


if __name__ == '__main__':
    cli(max_content_width=120)
