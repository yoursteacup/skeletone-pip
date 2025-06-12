# Skeletone

A minimal, well-structured Python project skeleton and **micro-framework** for rapid backend development.  
Built on top of **FastAPI**, **SQLAlchemy**, and **Alembic** with automated template versioning and logging.

## Features

- 🚀 **FastAPI** foundation with modern Python async practices
- 🗄️ **SQLAlchemy (async)** ORM with **Alembic** migrations
- 🧩 **Minimal framework structure** with clear folder layout
- 📦 **Template management**: init, upgrade, downgrade, version lock
- 📄 **Patch-based updates** between template versions
- 🔁 **Incremental version tracking** via `skeletone.lock`
- 📊 **Request logging**: Incoming API requests are logged to a database
- 🧾 **Custom logging module** for easy integration and extension
- ⚡ **Quick setup** - get started in seconds

## Installation

```bash
pip install skeletone
```

## Quick Start

### 1. Initialize a New Project

```bash
mkdir my-awesome-api && cd my-awesome-api
skeletone init
```

### 2. Check Available Versions

```bash
skeletone versions
```

### 3. Upgrade Your Project

```bash
skeletone upgrade
```

### 4. Rollback if Needed

```bash
# Interactive version selection
skeletone downgrade

# Or specify version directly
skeletone downgrade -v v1.2.0
```

## CLI Commands

| Command             | Description                                |
|---------------------|--------------------------------------------|
| `skeletone init`     | Initialize new project from latest template |
| `skeletone upgrade`  | Upgrade to latest template version         |
| `skeletone downgrade`| Downgrade to a previous template version   |
| `skeletone versions` | List all available template versions       |
| `skeletone help`     | Show detailed help and usage examples      |

## How It Works

Skeletone is built around a **patch-based versioning system**:

- **Init**: Sets up a fresh project from the latest template
- **Upgrade**: Applies sequential `.patch` diffs to upgrade your project
- **Downgrade**: Applies reverse patches to safely revert
- **Track**: Saves current version to `skeletone.lock`

## Template Highlights

The generated project includes:

```
your-project/
├── app/
│   ├── models/         # SQLAlchemy models (async)
│   ├── routes/         # FastAPI route handlers
│   ├── dependencies/   # DI system
│   └── logging/        # Logging logic
├── alembic/            # Database migrations
├── config.py           # App settings
├── main.py             # FastAPI application entrypoint
├── requirements.txt    # Dependencies
└── skeletone.lock      # Template version lock file
```

## Logging System

Skeletone includes:

- 📥 **Request logger**: Automatically logs all incoming HTTP requests (path, method, status, timestamp)
- 🧾 **Logging module**: Easily extendable and stored logs in the **database**
- 🔍 Useful for debugging, monitoring, and auditing

All logging is **asynchronous**, just like the rest of the application.

## Example Workflow

```bash
# Create and initialize a new project
mkdir blog-api && cd blog-api
skeletone init

# Do your development work...

# Upgrade to latest version
skeletone upgrade

# Check available versions
skeletone versions

# Rollback if needed
skeletone downgrade -v v1.1.0
```

### Version Table Example

```text
Available Skeletone Versions
┌─────────┬─────────────┐
│ Version │ Status      │
├─────────┼─────────────┤
│ v1.3.0  │ ✅ Current   │
│ v1.2.0  │             │
│ v1.1.0  │             │
└─────────┴─────────────┘
```

## Best Practices

1. **Always commit** your code before upgrade/downgrade
2. **Review diffs** and changes after updating
3. **Thoroughly test** after version transitions
4. **Track your modifications** to avoid patch conflicts

## Template Repository

The base template for Skeletone lives here:  
👉 **[https://github.com/yoursteacup/skeletone](https://github.com/yoursteacup/skeletone)**

## Contributing

Contributions are welcome! Please see the GitHub repo for guidelines and issue tracking.

## Author

**Developer**: Zhaxybayev Daulet  
**GitHub**: [yoursteacup](https://github.com/yoursteacup)
