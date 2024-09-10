import os
import sys
from typing import Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.traceback import install

# Install rich traceback handler
install()

# Add the current directory to sys.path to ensure we can import the performance agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.performance_agent import analyze_codebase_performance

# Initialize Rich console for better formatting
console = Console()

def format_results(results: Optional[Dict[str, Any]]) -> None:
    """Format and display the performance analysis results using Rich."""
    if not results:
        console.print("❌ No performance analysis results to display.")
        return

    console.print("✅ Formatting performance analysis results:")

    # Create a table for the main categories
    table = Table(title="Performance and Security Analysis", expand=True)
    table.add_column("Category", style="cyan")
    table.add_column("Issues", style="magenta")

    categories = [
        ("Algorithmic Efficiency Issues", "algorithmicEfficiencyIssues"),
        ("Resource Utilization Vulnerabilities", "resourceUtilizationVulnerabilities"),
        ("Caching Security Implications", "cachingSecurityImplications"),
        ("Database Performance Risks", "databasePerformanceRisks"),
        ("Asynchronous Operation Concerns", "asynchronousOperationConcerns"),
        ("Third-Party Performance Security Risks", "thirdPartyPerformanceSecurityRisks"),
        ("Critical Performance Security Issues", "criticalPerformanceSecurityIssues")
    ]

    has_issues = False
    for category_name, category_key in categories:
        issues = results.get(category_key, [])
        if issues:
            has_issues = True
            for issue in issues:
                table.add_row(category_name, issue)
        else:
            table.add_row(category_name, "No issues found")

    if has_issues:
        console.print(table)
    else:
        console.print("[green]No significant performance issues found.[/green]")

    # Load Handling Security Impact
    console.print(Panel(f"[bold]Load Handling Security Impact:[/bold]\n{results.get('loadHandlingSecurityImpact', 'N/A')}"))

    # Overall Performance Security Risk
    console.print(f"[bold]Overall Performance Security Risk:[/bold] {results.get('overallPerformanceSecurityRisk', 'N/A')}")

    # Key Recommendations
    if results.get('keyRecommendations'):
        console.print("[bold]Key Recommendations:[/bold]")
        for recommendation in results['keyRecommendations']:
            console.print(f"• {recommendation}")
    else:
        console.print("[yellow]No specific recommendations provided.[/yellow]")

def main():
    console.print("🚀 Starting performance analysis tool...")
    
    current_dir = os.getcwd()
    console.print(f"🔍 Analyzing project performance in: {current_dir}")
    
    try:
        with console.status("[bold green]Analyzing project performance...[/bold green]"):
            results = analyze_codebase_performance(current_dir)
        
        if results:
            console.print("✅ Performance analysis complete!")
            format_results(results)
        else:
            console.print("[yellow]⚠️ No significant performance issues detected or analysis couldn't be completed.[/yellow]")
            console.print("This could mean:")
            console.print("1. The project has no significant performance issues.")
            console.print("2. The codebase is too small or simple for meaningful performance analysis.")
            console.print("3. The analysis couldn't access or process some parts of the codebase.")
    
    except Exception as e:
        console.print("[bold red]❌ An error occurred during performance analysis:[/bold red]")
        console.print(f"[red]{str(e)}[/red]")
        console.print("\n[bold]Traceback:[/bold]")
        console.print_exception(show_locals=True)

if __name__ == "__main__":
    main()
    console.print("👋 Thank you for using the performance analysis tool!")