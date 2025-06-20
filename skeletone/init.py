import json
import os
import subprocess
import tempfile
from shutil import copy2, copytree, rmtree

from git import Repo
from rich.console import Console

from skeletone.patches import patch_alembic_env, patch_env_example

console = Console()

SKELETON_REPO = "https://github.com/yoursteacup/skeletone"
PROJECT_PATH = os.getcwd()

def init_skeletone():
    with tempfile.TemporaryDirectory() as temp_dir:
        console.print(f"[bold green]Cloning template into temp dir: {temp_dir}[/bold green]")
        console.print(f"Cloning to temp_dir={temp_dir}, PROJECT_PATH={PROJECT_PATH}")
        Repo.clone_from(SKELETON_REPO, temp_dir, multi_options=["--depth=1", "--tags", "--no-single-branch"])

        # Searching latest tag
        repo = Repo(temp_dir)
        tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
        latest_tag = str(tags[-1])

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

        readme = os.path.join(temp_dir, "README.md")
        if os.path.exists(readme):
            os.remove(readme)
        patches = os.path.join(temp_dir, "patches")
        if os.path.exists(patches):
            rmtree(patches)
        release_script = os.path.join(temp_dir, "release.sh")
        if os.path.exists(release_script):
            os.remove(release_script)

        console.print("[bold green]Template copied to current directory (overwriting existing files).[/bold green]")

    # Applying version lock
    lock = {
        "template_repo": SKELETON_REPO,
        "template_version": latest_tag
    }
    with open(os.path.join(PROJECT_PATH, "skeletone.lock"), "w") as f:
        json.dump(lock, f, indent=2)

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

    env_example = os.path.join(PROJECT_PATH, ".env.example")
    project_name = os.path.basename(PROJECT_PATH)
    patch_env_example(env_example, project_name)

    console.print("[bold green]Ready![/bold green]")