import click


@click.group(short_help="auscope_theme CLI.")
def auscope_theme():
    """auscope_theme CLI.
    """
    pass


@auscope_theme.command()
@click.argument("name", default="auscope_theme")
def command(name):
    """Docs.
    """
    click.echo("Hello, {name}!".format(name=name))


def get_commands():
    return [auscope_theme]
