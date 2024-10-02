from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from .api_client import ButterflyAPIClient

console = Console()

def display_welcome_message():
    """Display a welcome message for Butterfly CLI."""
    welcome_message = Panel.fit(
        "[bold magenta]Butterfly[/bold magenta]\n"
        "[cyan]Your Security Blanket[/cyan]",
        border_style="bright_magenta"
    )
    console.print(welcome_message)

def prompt_for_api_key():
    """Prompt the user for their Butterfly API key."""
    api_key = Prompt.ask(
        "[yellow]Enter your API key[/yellow]",
        password=True
    )
    return api_key

def validate_api_key(api_key):
    """Validate the provided API key."""
    client = ButterflyAPIClient()
    client.api_key = api_key
    if client.validate_api_key():
        console.print("[green]API key validated.[/green]")
        return True
    else:
        console.print("[red]Invalid API key. Please try again.[/red]")
        return False

def display_initialization_success():
    """Display a success message after Butterfly initialization."""
    success_message = Panel.fit(
        "[bold green]Butterfly initialized successfully.[/bold green]\n"
        "[cyan]We are running in the background, you can continue development.[/cyan]",
        border_style="green"
    )
    console.print(success_message)