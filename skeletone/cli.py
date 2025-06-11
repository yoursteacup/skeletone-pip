import sys
print("RUNNING CLI.PY FROM:", __file__)
print("sys.argv:", sys.argv)

import os
import subprocess
from shutil import rmtree, copytree, copy2
import tempfile

import click
from git import Repo
from rich.console import Console

console = Console()

SKELETON_REPO = "https://github.com/yoursteacup/skeletone"
PROJECT_PATH = os.getcwd()

@click.group()
def main():
    pass

@main.command()
def init():
    """
    Initializing skeletone repo
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        console.print(f"[bold green]Cloning template into temp dir: {temp_dir}[/bold green]")
        console.print(f"Cloning to temp_dir={temp_dir}, PROJECT_PATH={PROJECT_PATH}")
        Repo.clone_from(SKELETON_REPO, temp_dir, multi_options=["--depth=1"])

        # Remove .git to detach template history
        rmtree(os.path.join(temp_dir, ".git"), ignore_errors=True)

        # Copy contents from temp_dir to PROJECT_PATH, overwriting
        for item in os.listdir(temp_dir):
            s = os.path.join(temp_dir, item)
            d = os.path.join(PROJECT_PATH, item)
            if os.path.isdir(s):
                if os.path.exists(d):
                    rmtree(d)
                copytree(s, d)
            else:
                copy2(s, d)

        console.print("[bold green]Template copied to current directory (overwriting existing files).[/bold green]")

    req_path = os.path.join(PROJECT_PATH, "requirements.txt")
    if os.path.exists(req_path):
        console.print(f"[bold green]Installing requirements: {req_path}[/bold green]")
        subprocess.run(["pip", "install", "-r", req_path], check=True)
        subprocess.run(["alembic", "init", "alembic"], check=True)
    else:
        console.print("[bold yellow]requirements.txt not found![/bold_yellow]")

    # Setting alembic
    alembic_env = os.path.join(PROJECT_PATH, "alembic", "env.py")
    if os.path.exists(alembic_env):
        console.print("[bold green]Setting up alembic[/bold green]")
        patch_alembic_env(alembic_env)
    else:
        console.print("[bold yellow]alembic/env.py not found![/bold yellow]")

    console.print("[bold green]Ready![/bold green]")

def patch_alembic_env(env_path):
    console.print("[light_salmon1]Patching imports...[/[light_salmon1]]")
    patch_alembic_imports(env_path)
    console.print("[light_salmon1]Patching settings...[/[light_salmon1]]")
    patch_alembic_settings(env_path)
    console.print("[light_salmon1]Patching metadata...[/[light_salmon1]]")
    patch_alembic_metadata(env_path)

def patch_alembic_metadata(env_path):
    with open(env_path, "r") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip() == "target_metadata = None":
            lines[i] = "target_metadata = Base.metadata\n"
            break

    with open(env_path, "w") as f:
        f.writelines(lines)

def patch_alembic_settings(env_path):
    with open(env_path, "r") as f:
        lines = f.readlines()

    insert_index = next(
        (i for i, line in enumerate(lines) if line.strip() == "config = context.config"),
        11
    )

    new_settings = [
        "db_settings = settings.database\n",
        "DATABASE_URL = (\n",
        '   f"postgresql+psycopg2://{db_settings.username}:{db_settings.password}"\n',
        '   f"@{db_settings.host}:{db_settings.port}/{db_settings.database}"\n',
        ")\n",
        'config.set_main_option("sqlalchemy.url", DATABASE_URL)'
    ]

    for i, new_import in enumerate(new_settings):
        lines.insert(insert_index + 1 + i, new_import)

    with open(env_path, "w") as f:
        f.writelines(lines)


def patch_alembic_imports(env_path):
    with open(env_path, "r") as f:
        lines = f.readlines()

    last_import_index = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("from"):
            last_import_index = i

    new_imports = [
        "from app.models.base import Base\n",
        "from config import settings\n"
    ]

    insert_index = last_import_index + 1 if last_import_index != 0 else last_import_index
    for i, new_import in enumerate(new_imports):
        lines.insert(insert_index + i, new_import)

    with open(env_path, "w") as f:
        f.writelines(lines)
