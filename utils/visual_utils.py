import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.table import Table
from rich import box

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