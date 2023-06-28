import click


@click.group(short_help="aorc_transposition CLI.")
def aorc_transposition():
    """aorc_transposition CLI.
    """
    pass


@aorc_transposition.command()
@click.argument("name", default="aorc_transposition")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [aorc_transposition]
