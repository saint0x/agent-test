import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import fnmatch

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the system prompt from .env
DEPENDENCY_SYS_PROMPT = os.getenv("DEPENDENCY_SYS_PROMPT")

def analyze_dependencies(file_paths, file_contents):
    """
    Analyze the dependencies of the project using the OpenAI API, with a focus on security.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "report_dependency_security_analysis",
                "description": "Report the dependency analysis of the project with security considerations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "knownVulnerabilities": {"type": "array", "items": {"type": "string"}},
                        "outdatedDependencies": {"type": "array", "items": {"type": "string"}},
                        "unmaintainedDependencies": {"type": "array", "items": {"type": "string"}},
                        "licensingSecurityIssues": {"type": "array", "items": {"type": "string"}},
                        "nestedVulnerabilities": {"type": "array", "items": {"type": "string"}},
                        "dependencyAuthenticityIssues": {"type": "array", "items": {"type": "string"}},
                        "increasedAttackSurface": {"type": "array", "items": {"type": "string"}},
                        "updateBarriers": {"type": "array", "items": {"type": "string"}},
                        "criticalDependencySecurityIssues": {"type": "array", "items": {"type": "string"}},
                        "overallDependencySecurityRisk": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
                        "keyRecommendations": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["overallDependencySecurityRisk", "keyRecommendations"]
                }
            }
        }
    ]

    # Prepare the content for analysis
    content = "\n\n".join([f"File: {path}\n\nContent:\n{content}" for path, content in zip(file_paths, file_contents)])

    messages = [
        {"role": "system", "content": DEPENDENCY_SYS_PROMPT},
        {"role": "user", "content": f"Analyze the dependencies and their security implications of the following project:\n\n{content}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        if tool_call.function.name == "report_dependency_security_analysis":
            return json.loads(tool_call.function.arguments)
    
    return None

def should_analyze_file(file_path):
    """
    Determine if a file should be analyzed based on its name and extension.
    """
    # List of file patterns to analyze
    patterns_to_analyze = [
        'package.json', 'package-lock.json', 'yarn.lock',  # Node.js
        'requirements.txt', 'Pipfile', 'Pipfile.lock',  # Python
        'pom.xml', 'build.gradle', 'build.gradle.kts',  # Java
        'Gemfile', 'Gemfile.lock',  # Ruby
        'composer.json', 'composer.lock',  # PHP
        'go.mod', 'go.sum',  # Go
        '*.csproj', 'packages.config',  # .NET
        'Cargo.toml', 'Cargo.lock',  # Rust
        'pubspec.yaml',  # Dart/Flutter
    ]

    return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns_to_analyze)

def analyze_project_dependencies(base_path):
    """
    Analyze the dependencies of all relevant files in a project, considering security implications.
    """
    file_paths = []
    file_contents = []
    for root, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            if should_analyze_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    file_paths.append(file_path)
                    file_contents.append(file_content)
                except Exception as e:
                    print(f"Error reading file {file_path}: {str(e)}")
    
    return analyze_dependencies(file_paths, file_contents)

def main():
    # Example usage
    base_path = "."  # Current directory
    results = analyze_project_dependencies(base_path)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()