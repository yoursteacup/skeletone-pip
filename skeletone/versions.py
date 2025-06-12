import json
import os

import requests
from rich.console import Console
from rich.table import Table

console = Console()

PROJECT_PATH = os.getcwd()


def get_current_version():
    """
    Get current version from skeletone.lock
    """
    lock_file = os.path.join(PROJECT_PATH, "skeletone.lock")
    if not os.path.exists(lock_file):
        return None

    try:
        with open(lock_file) as f:
            lock = json.load(f)
        return lock["template_version"]
    except (json.JSONDecodeError, KeyError):
        return None


def get_available_versions():
    """
    Get list of all available versions (tags) from repository
    """
    api_url = "https://api.github.com/repos/yoursteacup/skeletone/tags"
    try:
        r = requests.get(api_url, timeout=10)
        if r.status_code != 200:
            raise Exception(f"Cannot get versions list: {r.text}")

        tags = r.json()
        versions = [tag["name"] for tag in tags]
        return sorted(versions, reverse=True)  # Sort from newest to oldest
    except requests.RequestException as e:
        raise Exception(f"Network error when fetching versions: {e}")


def list_versions():
    """
    Display all available versions in a nice table format
    """
    try:
        current_version = get_current_version()
        versions = get_available_versions()

        if not versions:
            console.print("[bold red]No versions found![/bold red]")
            return

        # Create table
        table = Table(title="Available Skeletone Versions")
        table.add_column("Version", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")

        for version in versions:
            if version == current_version:
                table.add_row(version, "✅ Current")
            else:
                table.add_row(version, "")

        console.print(table)

        if current_version:
            console.print(f"\n[bold blue]Current version: {current_version}[/bold blue]")
        else:
            console.print("\n[bold yellow]No skeletone project detected in current directory[/bold yellow]")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")