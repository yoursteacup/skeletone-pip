import json
import os
import re
import subprocess

import requests
from rich.console import Console
from rich.prompt import Prompt

console = Console()

SKELETON_REPO = "https://github.com/yoursteacup/skeletone"
PROJECT_PATH = os.getcwd()
PATCHES_BASE_URL = "https://raw.githubusercontent.com/yoursteacup/skeletone/main/patches/"


def get_available_versions():
    """
    Fetching list of available versions (tags) from git
    """
    api_url = "https://api.github.com/repos/yoursteacup/skeletone/tags"
    r = requests.get(api_url)
    if r.status_code != 200:
        raise Exception(f"Could not fetch versions: {r.text}")

    tags = r.json()
    versions = [tag["name"] for tag in tags]
    return sorted(versions, reverse=True)  # Сортируем от новых к старым


def get_current_version():
    """
    Getting current version from skeletone.lock
    """
    lock_file = os.path.join(PROJECT_PATH, "skeletone.lock")
    if not os.path.exists(lock_file):
        raise Exception("File skeletone.lock not found. Project wasn't initialized with skeletone.")

    with open(lock_file) as f:
        lock = json.load(f)
    return lock["template_version"]


def get_all_patch_names():
    """
    Fetching patches names from git
    """
    api_url = "https://api.github.com/repos/yoursteacup/skeletone/contents/patches"
    r = requests.get(api_url)
    if r.status_code != 200:
        raise Exception(f"Could not fetch patches list: {r.text}")
    files = r.json()
    patch_names = [f["name"] for f in files if f["name"].endswith(".patch")]
    return sorted(patch_names)


def build_downgrade_patch_chain(current_ver, target_ver, patch_names):
    """
    Building chain of patches to downgrade from current_ver to target_ver
    """
    chain = []
    cur_ver = current_ver

    while cur_ver != target_ver:
        found = False
        for fname in patch_names:
            m = re.match(rf"(v[\d\.]+)_to_{re.escape(cur_ver)}\.patch$", fname)
            if m:
                prev_ver = m.group(1)
                chain.append((fname, prev_ver))
                cur_ver = prev_ver
                found = True
                break

        if not found:
            raise Exception(f"Downgrade chain from {current_ver} to {target_ver} was not found")

    return chain


def download_and_apply_reverse_patch(patch_name):
    """
    Downloading and applying reverse patches
    """
    url = PATCHES_BASE_URL + patch_name
    console.print(f"[bold green]⬇ Downloading patch: {patch_name}[/bold green]")
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"Could not download patch {patch_name}")

    patch_file = "tmp_skeletone_downgrade.patch"
    with open(patch_file, "wb") as f:
        f.write(r.content)

    result = subprocess.run(["git", "apply", "--whitespace=nowarn", "--reverse", patch_file],
                            capture_output=True, text=True)
    os.remove(patch_file)

    if result.returncode != 0:
        raise Exception(f"❌ Conflict during reverse patch {patch_name}!")


def downgrade_to_version(target_version):
    """
    Downgrading to target version in reverse
    """
    current_version = get_current_version()

    if current_version == target_version:
        console.print(f"[bold yellow]You currently on {target_version}[/bold yellow]")
        return

    available_versions = get_available_versions()
    if target_version not in available_versions:
        console.print(f"[bold red]Version {target_version} was not found![/bold red]")
        console.print(f"Available versions: {', '.join(available_versions)}")
        return

    try:
        patch_names = get_all_patch_names()
        chain = build_downgrade_patch_chain(current_version, target_version, patch_names)

        if not chain:
            console.print("[bold green]Already on target version[/bold green]")
            return

        console.print(f"[bold blue]Downgrade patch len: {len(chain)} patches[/bold blue]")

        for patch_name, prev_ver in chain:
            console.print(f"[bold green]⏪ Applying reverse patch: {patch_name}[/bold green]")
            download_and_apply_reverse_patch(patch_name)

            lock = {
                "template_repo": SKELETON_REPO,
                "template_version": prev_ver
            }
            with open(os.path.join(PROJECT_PATH, "skeletone.lock"), "w") as f:
                json.dump(lock, f, indent=2)

            console.print(f"[bold green]✅ Downgraded to {prev_ver}[/bold green]")

        console.print(f"[bold green]🎉 Successfully downgraded to {target_version}![/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ Error during downgrade: {e}[/bold red]")
        console.print("[bold yellow]Manual conflict resolving is possible[/bold yellow]")


def list_available_versions():
    """
    Show available versions list
    """
    try:
        current_version = get_current_version()
        versions = get_available_versions()

        console.print("[bold blue]📋 Available versions:[/bold blue]")
        for version in versions:
            if version == current_version:
                console.print(f"  {version} [bold green](current)[/bold green]")
            else:
                console.print(f"  {version}")

    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


def downgrade_skeletone(target_version=None):
    """
    Main downgrade method
    """
    try:
        if target_version is None:
            list_available_versions()
            target_version = Prompt.ask("\nInput version for downgrade")

        downgrade_to_version(target_version)

    except Exception as e:
        console.print(f"[bold red]❌ Error during downgrade: {e}[/bold red]")