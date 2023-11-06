import click


@click.group(short_help="igsn_theme CLI.")
def igsn_theme():
    """igsn_theme CLI.
    """
    pass


@igsn_theme.command()
@click.argument("name", default="igsn_theme")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [igsn_theme]
