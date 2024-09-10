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
PERFORMANCE_SYS_PROMPT = os.getenv("PERFORMANCE_SYS_PROMPT")

def analyze_performance(file_paths, file_contents):
    """
    Analyze the performance of the codebase, with a focus on security.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "report_performance_security_analysis",
                "description": "Report the performance analysis of the codebase with security considerations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "algorithmicEfficiencyIssues": {"type": "array", "items": {"type": "string"}},
                        "resourceUtilizationVulnerabilities": {"type": "array", "items": {"type": "string"}},
                        "cachingSecurityImplications": {"type": "array", "items": {"type": "string"}},
                        "databasePerformanceRisks": {"type": "array", "items": {"type": "string"}},
                        "asynchronousOperationConcerns": {"type": "array", "items": {"type": "string"}},
                        "loadHandlingSecurityImpact": {"type": "string"},
                        "thirdPartyPerformanceSecurityRisks": {"type": "array", "items": {"type": "string"}},
                        "criticalPerformanceSecurityIssues": {"type": "array", "items": {"type": "string"}},
                        "overallPerformanceSecurityRisk": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
                        "keyRecommendations": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["overallPerformanceSecurityRisk", "keyRecommendations"]
                }
            }
        }
    ]

    # Prepare the content for analysis
    content = "\n\n".join([f"File: {path}\n\nContent:\n{content}" for path, content in zip(file_paths, file_contents)])

    messages = [
        {"role": "system", "content": PERFORMANCE_SYS_PROMPT},
        {"role": "user", "content": f"Analyze the performance and security implications of the following codebase:\n\n{content}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        if tool_call.function.name == "report_performance_security_analysis":
            return json.loads(tool_call.function.arguments)
    
    return None

def should_analyze_file(file_path):
    """
    Determine if a file should be analyzed based on its extension and name.
    """
    # List of file extensions and patterns to analyze
    patterns_to_analyze = [
        '*.py', '*.js', '*.ts', '*.php', '*.rb', '*.java', '*.go', '*.cs',  # Backend code
        '*.sql',  # Database scripts
        'Dockerfile', 'docker-compose.yml',  # Docker files
        'package.json', 'requirements.txt', 'Gemfile', 'pom.xml',  # Package managers
        '.htaccess', 'nginx.conf', 'web.config',  # Server configurations
        '*.swift', '*.kt'  # Mobile app source
    ]

    return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns_to_analyze)

def analyze_codebase_performance(base_path):
    """
    Analyze the performance of all relevant files in a codebase, considering security implications.
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
    
    return analyze_performance(file_paths, file_contents)

def main():
    # Example usage
    base_path = "."  # Current directory
    results = analyze_codebase_performance(base_path)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()