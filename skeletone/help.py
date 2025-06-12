from rich.console import Console

console = Console()

def show_help():
    """Display comprehensive help information"""
    console.print("""
    [bold cyan]Skeletone - Python Project Template Manager[/bold cyan]
    
    [bold yellow]COMMANDS:[/bold yellow]
    - skeletone init         Initialize new project
    - skeletone upgrade      Upgrade to latest version  
    - skeletone downgrade    Downgrade to specific version
    - skeletone versions     List all available versions
    - skeletone help         Show this help
    
    [bold yellow]EXAMPLES:[/bold yellow]
    skeletone init
    skeletone upgrade  
    skeletone downgrade -v v1.2.0
    skeletone versions
    """)