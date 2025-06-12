import json
import os
import re
import subprocess

import requests
from rich.console import Console

console = Console()

PATCHES_BASE_URL = "https://raw.githubusercontent.com/yoursteacup/skeletone/main/patches/"

def get_all_patch_names():
    """
    Fetching patches names with GitHub API
    """
    api_url = "https://api.github.com/repos/yoursteacup/skeletone/contents/patches"
    r = requests.get(api_url)
    if r.status_code != 200:
        raise Exception(f"Could not fetch patches list: {r.text}")
    files = r.json()
    patch_names = [f["name"] for f in files if f["name"].endswith(".patch")]
    return sorted(patch_names)

def build_patch_chain(cur_ver, patch_names):
    chain = []
    while True:
        found = False
        for fname in patch_names:
            m = re.match(rf"{re.escape(cur_ver)}_to_(v[\d\.]+)\.patch$", fname)
            if m:
                next_ver = m.group(1)
                chain.append((fname, next_ver))
                cur_ver = next_ver
                found = True
                break
        if not found:
            break
    return chain

def download_and_apply_patch(patch_name):
    url = PATCHES_BASE_URL + patch_name
    console.print(f"[bold green]⬇ Downloading patch: {url}[/bold green]")
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"Can't download patch {patch_name}")
    with open("tmp_skeletone_upgrade.patch", "wb") as f:
        f.write(r.content)
    result = subprocess.run(["git", "apply", "--whitespace=nowarn", "tmp_skeletone_upgrade.patch"],
                            capture_output=True, text=True)
    os.remove("tmp_skeletone_upgrade.patch")
    if result.returncode != 0:
        raise Exception(f"❌ Patch conflict {patch_name}!")

def upgrade_skeletone():
    console.print("[bold green]Running upgrade...[/bold green]")
    with open("skeletone.lock") as f:
        lock = json.load(f)
    cur_ver = lock["template_version"]

    patch_names = get_all_patch_names()
    chain = build_patch_chain(cur_ver, patch_names)

    if not chain:
        console.print("[bold green]No patches required[/bold green]")
        return

    for patch_name, next_ver in chain:
        console.print(f"[bold green]⏩ Applying patch: {patch_name}[/bold green]")
        download_and_apply_patch(patch_name)
        lock["template_version"] = next_ver
        with open("skeletone.lock", "w") as f:
            json.dump(lock, f, indent=2)
        console.print(f"[bold green]✅ Patched to version {next_ver}[/bold green]")

    console.print("[bold green]Patch complete[/bold green]")
