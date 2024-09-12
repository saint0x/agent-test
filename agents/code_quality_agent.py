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
CODE_QUALITY_SYS_PROMPT = os.getenv("CODE_QUALITY_SYS_PROMPT")

class CodeQualityAgent:
    def __init__(self):
        self.client = client
        self.system_prompt = CODE_QUALITY_SYS_PROMPT

    def analyze_code_quality(self, file_paths, file_contents):
        """
        Analyze the code quality of the codebase.
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "report_code_quality_analysis",
                    "description": "Report the code quality analysis of the codebase",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "readabilityAssessment": {"type": "string"},
                            "codeDuplicationIssues": {"type": "array", "items": {"type": "string"}},
                            "complexityIssues": {"type": "array", "items": {"type": "string"}},
                            "namingConventionViolations": {"type": "array", "items": {"type": "string"}},
                            "errorHandlingAssessment": {"type": "string"},
                            "loggingPractices": {"type": "string"},
                            "testCoverageAssessment": {"type": "string"},
                            "codeOrganization": {"type": "string"},
                            "commentQuality": {"type": "string"},
                            "solidPrincipleAdherence": {"type": "string"},
                            "securityBestPractices": {"type": "string"},
                            "performanceConsiderations": {"type": "array", "items": {"type": "string"}},
                            "maintainabilityScore": {"type": "number", "minimum": 0, "maximum": 10},
                            "overallCodeQualityAssessment": {"type": "string", "enum": ["Poor", "Fair", "Good", "Excellent"]},
                            "keyRecommendations": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["readabilityAssessment", "overallCodeQualityAssessment", "maintainabilityScore", "keyRecommendations"]
                    }
                }
            }
        ]

        # Prepare the content for analysis
        content = "\n\n".join([f"File: {path}\n\nContent:\n{content}" for path, content in zip(file_paths, file_contents)])

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Analyze the code quality of the following codebase:\n\n{content}"}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call.function.name == "report_code_quality_analysis":
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
            '*.xml', '*.json',  # Configuration files
            '*.md', '*.txt'  # Documentation files
        ]

        return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns_to_analyze)

    def analyze_codebase_quality(self, base_path):
        """
        Analyze the code quality of all relevant files in a codebase.
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
        
        return self.analyze_code_quality(file_paths, file_contents)

def main():
    agent = CodeQualityAgent()
    base_path = "."  # Current directory
    results = agent.analyze_codebase_quality(base_path)
    
    # Wrap the results in a dictionary with the key "CODE_QUALITY_ANALYSIS"
    output = {"CODE_QUALITY_ANALYSIS": results}
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()