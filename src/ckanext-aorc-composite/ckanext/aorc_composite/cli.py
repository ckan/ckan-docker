import click


@click.group(short_help="aorc_composite CLI.")
def aorc_composite():
    """aorc_composite CLI.
    """
    pass


@aorc_composite.command()
@click.argument("name", default="aorc_composite")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [aorc_composite]
