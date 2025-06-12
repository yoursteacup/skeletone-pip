# Skeletone

A minimal, well-structured Python project skeleton for rapid development.  
Built on top of **FastAPI**, **SQLAlchemy**, and **Alembic** with automated template management.

## Features

- 🚀 **FastAPI** foundation with modern Python practices
- 🗄️ **SQLAlchemy** ORM with **Alembic** migrations  
- 📦 **Template Management** with automated upgrades/downgrades
- 🔄 **Incremental Updates** using patch-based system
- ⚡ **Quick Setup** - get started in seconds

## Installation

```bash
pip install skeletone
```

## Quick Start

### 1. Initialize New Project
```bash
mkdir my-awesome-api && cd my-awesome-api
skeletone init
```

### 2. Check Available Versions
```bash
skeletone versions
```

### 3. Keep Your Project Updated
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

## Commands

| Command | Description |
|---------|-------------|
| `skeletone init` | Initialize new project from latest template |
| `skeletone upgrade` | Upgrade to latest template version |
| `skeletone downgrade` | Downgrade to previous template version |
| `skeletone versions` | List all available template versions |
| `skeletone help` | Show detailed help and examples |

## How It Works

Skeletone uses a **patch-based system** for template management:

- **Initialization**: Downloads the latest template
- **Upgrades**: Applies incremental patches to update your project
- **Downgrades**: Uses reverse patches to safely rollback changes
- **Version Tracking**: Maintains version history in `skeletone.lock`

## Template Structure

The generated project includes:

```
your-project/
├── app/
│   ├── models/         # SQLAlchemy models
│   ├── routes/         # FastAPI routes
│   └── dependencies/   # Dependency injection
├── alembic/           # Database migrations
├── config.py          # Configuration management
├── main.py           # FastAPI application
├── requirements.txt  # Dependencies
└── skeletone.lock   # Version tracking
```

## Examples

### Complete Workflow
```bash
# Create and setup new project
mkdir blog-api && cd blog-api
skeletone init

# Start development...
# (build your amazing API)

# Update to latest template
skeletone upgrade

# Check what versions are available
skeletone versions

# Rollback if something breaks
skeletone downgrade -v v1.1.0
```

### Version Management
```bash
# See all available versions
skeletone versions

# Current output example:
# Available Skeletone Versions
# ┌─────────┬─────────────┐
# │ Version │ Status      │
# ├─────────┼─────────────┤
# │ v1.3.0  │ ✅ Current  │
# │ v1.2.0  │             │
# │ v1.1.0  │             │
# └─────────┴─────────────┘
```

## Best Practices

1. **Always commit your code** before running upgrades/downgrades
2. **Review changes** after template updates
3. **Test thoroughly** after version changes
4. **Use version control** to track your customizations

## Template Source

The project template itself is hosted at:  
**https://github.com/yoursteacup/skeletone**

## Contributing

Contributions are welcome! Please see the main repository for guidelines.

## Author

**Developer**: Zhaxybayev Daulet  
**Repository**: https://github.com/yoursteacup/skeletone