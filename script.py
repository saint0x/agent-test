import os
import json
import sqlite3
import logging
from agents.architecture_agent import ArchitectureAgent
from agents.code_quality_agent import CodeQualityAgent
from agents.dependency_agent import DependencyAgent
from agents.performance_agent import PerformanceAgent
from agents.static_agent import StaticAgent
from dotenv import load_dotenv
from api_generation.utils.db_utils import insert_user

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize agents
architecture_agent = ArchitectureAgent()
code_quality_agent = CodeQualityAgent()
dependency_agent = DependencyAgent()
performance_agent = PerformanceAgent()
static_agent = StaticAgent()

# Function to run all analyses and format results

def run_all_analyses():
    results = {}
    
    # Run each agent's analysis
    try:
        results['ARCHITECTURE_ANALYSIS'] = architecture_agent.analyze_codebase_architecture()
        print("[green]Architecture analysis completed successfully.[/green]")
    except Exception as e:
        print(f"[red]Error during architecture analysis: {str(e)}[/red]")

    try:
        results['CODE_QUALITY_ANALYSIS'] = code_quality_agent.analyze_codebase_quality()
        print("[green]Code quality analysis completed successfully.[/green]")
    except Exception as e:
        print(f"[red]Error during code quality analysis: {str(e)}[/red]")

    try:
        results['DEPENDENCY_AUDIT'] = dependency_agent.analyze_codebase_dependencies()
        print("[green]Dependency audit completed successfully.[/green]")
    except Exception as e:
        print(f"[red]Error during dependency audit: {str(e)}[/red]")

    try:
        results['PERFORMANCE_ANALYSIS'] = performance_agent.analyze_codebase_performance()
        print("[green]Performance analysis completed successfully.[/green]")
    except Exception as e:
        print(f"[red]Error during performance analysis: {str(e)}[/red]")

    try:
        results['STATIC_CODE_ANALYSIS'] = static_agent.analyze_codebase_static()
        print("[green]Static code analysis completed successfully.[/green]")
    except Exception as e:
        print(f"[red]Error during static code analysis: {str(e)}[/red]")

    # Format results into a JSON object
    formatted_results = json.dumps(results, indent=2)
    
    # Write results to json.json
    with open('json.json', 'w') as json_file:
        json_file.write(formatted_results)
        print("[green]Results written to json.json successfully.[/green]")

    # Append results to the database
    append_results_to_db(results)

# Function to append results to the database

def append_results_to_db(results):
    conn = sqlite3.connect('root.db')
    cursor = conn.cursor()

    for key, value in results.items():
        # Ensure value is a string for overallSummary
        overall_summary = value.get('summary', 'No summary available') if isinstance(value, dict) else 'No summary available'
        cursor.execute("INSERT INTO analysis_results (user_id, overallProjectHealth, overallSummary, formatted_report) VALUES (?, ?, ?, ?)", (1, key, overall_summary, json.dumps(value)))

    conn.commit()
    print("[green]Results appended to the database successfully.[/green]")
    conn.close()

# Function to insert API key into the database

def insert_api_key(api_key):
    logger.info(f"Inserting API key: {api_key}")  # Log the API key being inserted
    insert_user(api_key)  # Call the insert_user function to store the API key

if __name__ == '__main__':
    run_all_analyses()
    # Example of inserting an API key
    insert_api_key('your_api_key_here')  # Replace with the actual API key you want to insert
