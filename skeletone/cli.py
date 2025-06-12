import click

from skeletone.downgrade import downgrade_skeletone
from skeletone.help import show_help
from skeletone.init import init_skeletone
from skeletone.upgrade import upgrade_skeletone
from skeletone.versions import list_versions

@click.group()
def main():
    pass

@main.command()
def help():
    """Show detailed help and usage examples."""
    show_help()

@main.command()
def init():
    """
    Initializing skeletone repo
    """
    init_skeletone()

@main.command()
def upgrade():
    """Upgrade your project to the latest skeletone template version."""
    upgrade_skeletone()

@main.command()
@click.option("-v", "--version", help="Target tag to downgrade to")
def downgrade(version):
    """Downgrade your project to a specific skeletone template version."""
    downgrade_skeletone(target_version=version)

@main.command()
def versions():
    """List all available template versions."""
    list_versions()
