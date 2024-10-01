import os
import json
import threading
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.table import Table
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from agents.manager_agent import ManagerAgent  # Updated import
from utils.env_manager import set_api_key, get_api_key
from utils.config_manager import root, create_config_file, load_config, update_config
from utils.api_client import ButterflyAPIClient
from utils.api_key_manager import generate_and_store_api_key, validate_api_key
from utils.visual_utils import create_header, create_section, create_table, format_report

console = Console()

def run_background_analysis(manager_agent):
    while True:
        try:
            results = manager_agent.analyze_codebase()  # Call on instance
            # Process results (e.g., send to server, update local files, etc.)
            console.print("[green]Analysis completed successfully.[/green]")
        except Exception as e:
            console.print(f"[red]Error during analysis: {str(e)}[/red]")
        # Wait for some time before the next analysis
        threading.Event().wait(3600)  # Run every hour


def main():
    console.print(create_header())

    project_root = root()
    if not project_root:
        project_root = Path.cwd()
        create_config_file(project_root)
    
    config = load_config()
    
    api_key = get_api_key()
    if not api_key:
        console.print("[yellow]No API key found. Generating a new one...[/yellow]")
        api_key = generate_and_store_api_key()
        set_api_key(project_root, api_key)
        console.print(f"[green]New API key generated: {api_key}[/green]")
        console.print("[cyan]Please keep this key safe. You'll need it to use Butterfly.[/cyan]")

    if validate_api_key(api_key):
        console.print("[green]API key validated successfully.[/green]")
    else:
        console.print("[red]Invalid or expired API key. Please contact support for a new key.[/red]")
        return

    console.print("[cyan]Butterfly is now running in the background. You can continue your development.[/cyan]")

    manager_agent = ManagerAgent()  # Create an instance of ManagerAgent
    # Start background analysis
    threading.Thread(target=run_background_analysis, args=(manager_agent,), daemon=True).start()  # Pass instance

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[green]Analyzing codebase...", total=None)
        report_data = manager_agent.analyze_codebase()  # Call on instance
        progress.update(task, completed=True)

    console.log("Codebase analysis complete.")

    if "error" in report_data:
        console.print(f"[bold red]Error:[/bold red] {report_data['error']}")
        return

    console.log("Generating formatted report...")
    formatted_report = format_report(report_data)

    console.print(formatted_report)

    console.log("Printing summary panels...")
    console.print("\n")
    console.print(Panel.fit(
        Text("Overall Project Health: ", style="bold white") + Text(report_data.get('overallProjectHealth', 'Unknown'), style="bold green"),
        border_style="bright_magenta",
        title="Summary",
        subtitle="Butterfly Security"
    ))

    console.print("\n")
    console.print(Panel(
        Text(report_data.get('overallSummary', 'No summary available.'), style="italic"),
        border_style="cyan",
        title="Overall Summary",
        expand=False
    ))

    console.log("Report generation complete.")

    # Keep the main thread alive
    try:
        while True:
            threading.Event().wait(3600)
    except KeyboardInterrupt:
        console.print("[yellow]Butterfly analysis stopped.[/yellow]")

if __name__ == "__main__":
    main()