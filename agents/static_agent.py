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
STATIC_SYS_PROMPT = os.getenv("STATIC_SYS_PROMPT")

def analyze_file(file_path, file_content):
    """
    Analyze a single file, with a focus on security.
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "report_security_issue",
                "description": "Report a security issue found in the analyzed file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "fileName": {"type": "string"},
                        "fileType": {"type": "string"},
                        "criticalSecurityIssues": {"type": "array", "items": {"type": "string"}},
                        "majorSecurityConcerns": {"type": "array", "items": {"type": "string"}},
                        "sensitiveDataExposure": {"type": "array", "items": {"type": "string"}},
                        "securityBestPracticeViolations": {"type": "array", "items": {"type": "string"}},
                        "overallSecurityRisk": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
                        "keyRecommendations": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["fileName", "fileType", "overallSecurityRisk"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": STATIC_SYS_PROMPT},
        {"role": "user", "content": f"Analyze the following file:\n\nFile: {file_path}\n\nContent:\n{file_content}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        if tool_call.function.name == "report_security_issue":
            return json.loads(tool_call.function.arguments)
    
    return None

def should_analyze_file(file_path):
    """
    Determine if a file should be analyzed based on its extension and name.
    """
    # List of file extensions and patterns to analyze
    patterns_to_analyze = [
        '*.py', '*.js', '*.ts', '*.php', '*.rb', '*.java', '*.go', '*.cs',  # Backend code
        '*.env', '*.yml', '*.yaml', '*.json', '*.xml',  # Configuration files
        '*.sql',  # Database scripts
        'Dockerfile', 'docker-compose.yml',  # Docker files
        '.gitlab-ci.yml', '.travis.yml', '.github/workflows/*.yml',  # CI/CD configs
        'package.json', 'requirements.txt', 'Gemfile', 'pom.xml',  # Package managers
        '.htaccess', 'nginx.conf', 'web.config',  # Server configurations
        '*.swift', '*.kt'  # Mobile app source
    ]

    return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns_to_analyze)

def analyze_codebase(base_path):
    """
    Analyze all relevant files in a codebase.
    """
    security_reports = []
    for root, _, files in os.walk(base_path):
        for file in files:
            file_path = os.path.join(root, file)
            if should_analyze_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    report = analyze_file(file_path, file_content)
                    if report:
                        security_reports.append(report)
                except Exception as e:
                    print(f"Error analyzing file {file_path}: {str(e)}")
    return security_reports

def main():
    # Example usage
    base_path = "."  # Current directory
    results = analyze_codebase(base_path)
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()