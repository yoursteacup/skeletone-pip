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
    Получаем список всех доступных версий (тегов) из репозитория
    """
    api_url = "https://api.github.com/repos/yoursteacup/skeletone/tags"
    r = requests.get(api_url)
    if r.status_code != 200:
        raise Exception(f"Не удается получить список версий: {r.text}")

    tags = r.json()
    versions = [tag["name"] for tag in tags]
    return sorted(versions, reverse=True)  # Сортируем от новых к старым


def get_current_version():
    """
    Получаем текущую версию из skeletone.lock
    """
    lock_file = os.path.join(PROJECT_PATH, "skeletone.lock")
    if not os.path.exists(lock_file):
        raise Exception("Файл skeletone.lock не найден. Проект не инициализирован через skeletone.")

    with open(lock_file) as f:
        lock = json.load(f)
    return lock["template_version"]


def get_all_patch_names():
    """
    Получаем список всех патчей из репозитория
    """
    api_url = "https://api.github.com/repos/yoursteacup/skeletone/contents/patches"
    r = requests.get(api_url)
    if r.status_code != 200:
        raise Exception(f"Не удается получить список патчей: {r.text}")
    files = r.json()
    patch_names = [f["name"] for f in files if f["name"].endswith(".patch")]
    return sorted(patch_names)


def build_downgrade_patch_chain(current_ver, target_ver, patch_names):
    """
    Строим цепочку патчей для отката от current_ver к target_ver
    """
    chain = []
    cur_ver = current_ver

    while cur_ver != target_ver:
        found = False
        # Ищем патч, который приводит к текущей версии
        for fname in patch_names:
            m = re.match(rf"(v[\d\.]+)_to_{re.escape(cur_ver)}\.patch$", fname)
            if m:
                prev_ver = m.group(1)
                chain.append((fname, prev_ver))
                cur_ver = prev_ver
                found = True
                break

        if not found:
            raise Exception(f"Не найден путь отката от {current_ver} к {target_ver}")

    return chain


def download_and_apply_reverse_patch(patch_name):
    """
    Скачиваем и применяем патч в обратном порядке
    """
    url = PATCHES_BASE_URL + patch_name
    console.print(f"[bold green]⬇ Скачивание патча: {patch_name}[/bold green]")
    r = requests.get(url)
    if r.status_code != 200:
        raise Exception(f"Не удается скачать патч {patch_name}")

    patch_file = "tmp_skeletone_downgrade.patch"
    with open(patch_file, "wb") as f:
        f.write(r.content)

    # Применяем патч в обратном порядке (-R или --reverse)
    result = subprocess.run(["git", "apply", "--reverse", patch_file])
    os.remove(patch_file)

    if result.returncode != 0:
        raise Exception(f"❌ Конфликт при применении обратного патча {patch_name}!")


def downgrade_to_version(target_version, force=False):
    """
    Откатываемся к указанной версии используя обратные патчи
    """
    current_version = get_current_version()

    if current_version == target_version:
        console.print(f"[bold yellow]Вы уже используете версию {target_version}[/bold yellow]")
        return

    available_versions = get_available_versions()
    if target_version not in available_versions:
        console.print(f"[bold red]Версия {target_version} не найдена![/bold red]")
        console.print(f"Доступные версии: {', '.join(available_versions)}")
        return

    if not force:
        console.print(f"[bold yellow]⚠️  ВНИМАНИЕ: Откат с {current_version} на {target_version}[/bold yellow]")
        console.print("[bold yellow]Это действие откатит изменения с помощью обратных патчей![/bold yellow]")

        confirm = Prompt.ask(
            "Продолжить? (y/N)",
            choices=["y", "n", "yes", "no"],
            default="n"
        )

        if confirm.lower() not in ["y", "yes"]:
            console.print("[bold red]Откат отменен[/bold red]")
            return

    try:
        # Получаем список патчей и строим цепочку для отката
        patch_names = get_all_patch_names()
        chain = build_downgrade_patch_chain(current_version, target_version, patch_names)

        if not chain:
            console.print("[bold green]Уже на целевой версии[/bold green]")
            return

        console.print(f"[bold blue]Планируемый путь отката: {len(chain)} патчей[/bold blue]")

        # Применяем патчи в обратном порядке
        for patch_name, prev_ver in chain:
            console.print(f"[bold green]⏪ Применение обратного патча: {patch_name}[/bold green]")
            download_and_apply_reverse_patch(patch_name)

            # Обновляем skeletone.lock после каждого патча
            lock = {
                "template_repo": SKELETON_REPO,
                "template_version": prev_ver
            }
            with open(os.path.join(PROJECT_PATH, "skeletone.lock"), "w") as f:
                json.dump(lock, f, indent=2)

            console.print(f"[bold green]✅ Откачен до версии {prev_ver}[/bold green]")

        console.print(f"[bold green]🎉 Успешно откачен до версии {target_version}![/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ Ошибка при откате: {e}[/bold red]")
        console.print("[bold yellow]Возможно потребуется ручное разрешение конфликтов[/bold yellow]")


def list_available_versions():
    """
    Показываем список доступных версий
    """
    try:
        current_version = get_current_version()
        versions = get_available_versions()

        console.print("[bold blue]📋 Доступные версии:[/bold blue]")
        for version in versions:
            if version == current_version:
                console.print(f"  {version} [bold green](текущая)[/bold green]")
            else:
                console.print(f"  {version}")

    except Exception as e:
        console.print(f"[bold red]Ошибка: {e}[/bold red]")


def downgrade_skeletone(target_version=None, force=False):
    """
    Основная функция отката
    """
    try:
        if target_version is None:
            list_available_versions()
            target_version = Prompt.ask("\nВведите версию для отката")

        downgrade_to_version(target_version, force)

    except Exception as e:
        console.print(f"[bold red]❌ Ошибка при откате: {e}[/bold red]")