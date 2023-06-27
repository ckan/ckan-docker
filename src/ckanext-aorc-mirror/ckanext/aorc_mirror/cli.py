import click


@click.group(short_help="aorc_mirror CLI.")
def aorc_mirror():
    """aorc_mirror CLI.
    """
    pass


@aorc_mirror.command()
@click.argument("name", default="aorc_mirror")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [aorc_mirror]
