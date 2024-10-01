import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import fnmatch
from utils.config_manager import root as get_project_root
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the system prompt from .env
CODE_QUALITY_SYS_PROMPT = os.getenv("CODE_QUALITY_SYS_PROMPT")

class CodeQualityAnalysis(BaseModel):
    readabilityAssessment: str
    codeDuplicationIssues: list[str]
    complexityIssues: list[str]
    namingConventionViolations: list[str]
    errorHandlingAssessment: str
    loggingPractices: str
    testCoverageAssessment: str
    codeOrganization: str
    commentQuality: str
    solidPrincipleAdherence: str
    securityBestPractices: str
    performanceConsiderations: list[str]
    maintainabilityScore: float
    overallCodeQualityAssessment: str
    keyRecommendations: list[str]

class CodeQualityAgent:
    def __init__(self):
        self.client = client
        self.system_prompt = CODE_QUALITY_SYS_PROMPT

    def analyze_code_quality(self, file_paths, file_contents):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "report_code_quality_analysis",
                    "description": "Report the code quality analysis of the codebase",
                    "parameters": CodeQualityAnalysis.schema(),
                }
            }
        ]

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
                return CodeQualityAnalysis.parse_raw(tool_call.function.arguments)

        return None

    def should_analyze_file(self, file_path):
        patterns_to_analyze = [
            '*.py', '*.js', '*.ts', '*.php', '*.rb', '*.java', '*.go', '*.cs',
            '*.html', '*.css', '*.scss', '*.jsx', '*.tsx',
            '*.sql',
            'Dockerfile', 'docker-compose.yml',
            '*.xml', '*.json', '*.yaml', '*.yml',
            '*.c', '*.cpp', '*.h', '*.hpp',
            '*.rs', '*.scala', '*.kt', '*.swift'
        ]

        return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns_to_analyze)

    def analyze_codebase_quality(self):
        project_root = get_project_root()
        if not project_root:
            raise FileNotFoundError("butterfly.config.py not found in this or any parent directory")

        file_paths = []
        file_contents = []
        for root_dir, _, files in os.walk(project_root):
            for file in files:
                file_path = os.path.join(root_dir, file)
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
    results = agent.analyze_code_quality()
    output = {"CODE_QUALITY_ANALYSIS": results}
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()