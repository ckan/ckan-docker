import click

from ckanext.idsk.organization import ensure_default_organization


@click.group(short_help="IDSK portal commands")
def idsk():
    pass


@idsk.command("ensure-default-organization")
def ensure_default_organization_command():
    organization = ensure_default_organization()
    click.echo(f"Default organization ready: {organization['name']}")


def get_commands():
    return [idsk]
