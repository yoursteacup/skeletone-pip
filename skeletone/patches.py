from rich.console import Console

console = Console()


def patch_env_example(env_path, project_name):
    console.print("[light_salmon1]Patching .env.example...[/light_salmon1]")
    with open(env_path, "r") as f:
        lines = f.readlines()

    keys = ["POSTGRES_USERNAME", "POSTGRES_PASSWORD", "POSTGRES_DATABASE"]
    for key in keys:
        for i, line in enumerate(lines):
            if line.strip().startswith(f"{key}="):
                lines[i] = f"{key}={project_name}\n"

    with open(env_path, "w") as f:
        f.writelines(lines)

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
