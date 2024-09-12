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

class StaticAgent:
    def __init__(self):
        self.client = client
        self.system_prompt = STATIC_SYS_PROMPT

    def analyze_static_code(self, file_paths, file_contents):
        """
        Perform static code analysis on the codebase.
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "report_static_analysis",
                    "description": "Report the static code analysis results of the codebase",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "syntaxErrors": {"type": "array", "items": {"type": "string"}},
                            "potentialBugs": {"type": "array", "items": {"type": "string"}},
                            "securityVulnerabilities": {"type": "array", "items": {"type": "string"}},
                            "codeSmells": {"type": "array", "items": {"type": "string"}},
                            "styleViolations": {"type": "array", "items": {"type": "string"}},
                            "unusedCode": {"type": "array", "items": {"type": "string"}},
                            "complexityIssues": {"type": "array", "items": {"type": "string"}},
                            "potentialRuntimeErrors": {"type": "array", "items": {"type": "string"}},
                            "antiPatterns": {"type": "array", "items": {"type": "string"}},
                            "overallCodeHealth": {"type": "string", "enum": ["Poor", "Fair", "Good", "Excellent"]},
                            "keyRecommendations": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["overallCodeHealth", "keyRecommendations"]
                    }
                }
            }
        ]

        # Prepare the content for analysis
        content = "\n\n".join([f"File: {path}\n\nContent:\n{content}" for path, content in zip(file_paths, file_contents)])

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Perform static code analysis on the following codebase:\n\n{content}"}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call.function.name == "report_static_analysis":
                return json.loads(tool_call.function.arguments)
        
        return None

    def should_analyze_file(self, file_path):
        """
        Determine if a file should be analyzed based on its extension and name.
        """
        patterns_to_analyze = [
            '*.py', '*.js', '*.ts', '*.php', '*.rb', '*.java', '*.go', '*.cs',  # Backend code
            '*.html', '*.css', '*.scss', '*.jsx', '*.tsx',  # Frontend code
            '*.sql',  # Database scripts
            'Dockerfile', 'docker-compose.yml',  # Docker files
            '*.xml', '*.json', '*.yaml', '*.yml',  # Configuration files
            '*.c', '*.cpp', '*.h', '*.hpp',  # C/C++ files
            '*.rs',  # Rust files
            '*.scala',  # Scala files
            '*.kt',  # Kotlin files
            '*.swift',  # Swift files
            '*.sh', '*.bash',  # Shell scripts
            '*.ps1',  # PowerShell scripts
            '*.vue',  # Vue.js files
            '*.dart'  # Dart files
        ]

        return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns_to_analyze)

    def analyze_codebase_static(self, base_path):
        """
        Perform static code analysis on all relevant files in a codebase.
        """
        file_paths = []
        file_contents = []
        for root, _, files in os.walk(base_path):
            for file in files:
                file_path = os.path.join(root, file)
                if self.should_analyze_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        file_paths.append(file_path)
                        file_contents.append(file_content)
                    except Exception as e:
                        print(f"Error reading file {file_path}: {str(e)}")
        
        return self.analyze_static_code(file_paths, file_contents)

def main():
    agent = StaticAgent()
    base_path = "."  # Current directory
    results = agent.analyze_codebase_static(base_path)
    
    # Wrap the results in a dictionary with the key "STATIC_CODE_ANALYSIS"
    output = {"STATIC_CODE_ANALYSIS": results}
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()