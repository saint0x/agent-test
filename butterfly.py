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
from agents.manager_agent import analyze_codebase
from utils.env_manager import set_api_key, get_api_key
from utils.config_manager import root, create_config_file, load_config, update_config
from utils.api_client import ButterflyAPIClient
from utils.api_key_manager import generate_and_store_api_key, validate_api_key

console = Console()

def create_butterfly_swarm(width, height):
    butterflies = [
        "🦋", "🦋", "🦋", "🦋", "🦋",
        "🦋", "🦋", "🦋", "🦋", "🦋",
        "🦋", "🦋", "🦋", "🦋", "🦋",
        "🦋", "🦋", "🦋", "🦋", "🦋",
    ]
    swarm = [[" " for _ in range(width)] for _ in range(height)]
    for i, butterfly in enumerate(butterflies):
        x = i % width
        y = i // width
        if y < height:
            swarm[y][x] = butterfly
    return "\n".join("".join(row) for row in swarm)

def create_header():
    butterfly_swarm = create_butterfly_swarm(20, 3)
    title = Text("Butterfly Security Analysis", style="bold magenta")
    subtitle = Text("Transforming Your Code with Grace and Precision", style="italic cyan")
    header = Text.assemble(
        butterfly_swarm, "\n",
        title, "\n",
        subtitle, "\n",
        butterfly_swarm
    )
    return Panel(header, border_style="bright_magenta", box=box.DOUBLE)

def create_section(title, content):
    return Panel(
        Text(content),
        title=title,
        border_style="cyan",
        expand=False,
        title_align="left"
    )

def create_table(title, data):
    table = Table(title=title, box=box.ROUNDED, border_style="bright_blue", title_style="bold cyan")
    table.add_column("Key", style="magenta")
    table.add_column("Value", style="green")
    for key, value in data.items():
        if isinstance(value, list):
            value = "\n".join(f"• {item}" for item in value)
        table.add_row(key.capitalize(), str(value))
    return table

def format_report(report_data):
    console.log("Formatting report data...")
    layout = Layout()
    layout.split_column(
        Layout(name="header"),
        Layout(name="body", ratio=3)
    )
    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )

    layout["header"].update(create_header())

    left_column = Layout()
    right_column = Layout()

    sections = [
        ("Security Assessment", report_data.get('securityAssessment', {})),
        ("Code Quality Assessment", report_data.get('codeQualityAssessment', {})),
        ("Performance Assessment", report_data.get('performanceAssessment', {})),
    ]

    for title, data in sections:
        console.log(f"Creating table for {title}...")
        left_column.add_split(create_table(title, data))

    console.log("Creating tables for right column...")
    right_column.add_split(
        create_table("Architecture Assessment", report_data.get('architectureAssessment', {})),
        create_table("Dependency Assessment", report_data.get('dependencyAssessment', {})),
        create_section("Prioritized Action Items", "\n".join(f"{i+1}. {item}" for i, item in enumerate(report_data.get('prioritizedActionItems', []))))
    )

    layout["left"].update(left_column)
    layout["right"].update(right_column)

    console.log("Report formatting complete.")
    return layout

def run_background_analysis():
    while True:
        try:
            results = analyze_codebase()
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

    # Start background analysis
    threading.Thread(target=run_background_analysis, daemon=True).start()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[green]Analyzing codebase...", total=None)
        report_data = analyze_codebase()
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