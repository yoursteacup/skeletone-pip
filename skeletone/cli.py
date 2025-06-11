import click
from rich.console import Console

from skeletone.init import init_skeletone
from skeletone.upgrade import upgrade_skeletone

console = Console()

@click.group()
def main():
    pass

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
