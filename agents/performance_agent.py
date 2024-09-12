import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import fnmatch
from utils.config_manager import root as get_project_root

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the system prompt from .env
PERFORMANCE_SYS_PROMPT = os.getenv("PERFORMANCE_SYS_PROMPT")

class PerformanceAgent:
    def __init__(self):
        self.client = client
        self.system_prompt = PERFORMANCE_SYS_PROMPT

    def analyze_performance(self, file_paths, file_contents):
        """
        Analyze the performance of the codebase.
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "report_performance_analysis",
                    "description": "Report the performance analysis of the codebase",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "cpuIntensiveOperations": {"type": "array", "items": {"type": "string"}},
                            "memoryIntensiveOperations": {"type": "array", "items": {"type": "string"}},
                            "ioIntensiveOperations": {"type": "array", "items": {"type": "string"}},
                            "algorithmEfficiencyIssues": {"type": "array", "items": {"type": "string"}},
                            "databaseQueryPerformance": {"type": "array", "items": {"type": "string"}},
                            "scalabilityAssessment": {"type": "string"},
                            "concurrencyIssues": {"type": "array", "items": {"type": "string"}},
                            "cachingOpportunities": {"type": "array", "items": {"type": "string"}},
                            "networkCallOptimizations": {"type": "array", "items": {"type": "string"}},
                            "resourceLeaks": {"type": "array", "items": {"type": "string"}},
                            "overallPerformanceAssessment": {"type": "string", "enum": ["Poor", "Fair", "Good", "Excellent"]},
                            "estimatedResponseTimes": {"type": "object", "additionalProperties": {"type": "number"}},
                            "keyRecommendations": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["overallPerformanceAssessment", "keyRecommendations"]
                    }
                }
            }
        ]

        # Prepare the content for analysis
        content = "\n\n".join([f"File: {path}\n\nContent:\n{content}" for path, content in zip(file_paths, file_contents)])

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Analyze the performance of the following codebase:\n\n{content}"}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call.function.name == "report_performance_analysis":
                return json.loads(tool_call.function.arguments)
        
        return None

    def should_analyze_file(self, file_path):
        """
        Determine if a file should be analyzed based on its extension and name.
        """
        patterns_to_analyze = [
            '*.py', '*.js', '*.ts', '*.php', '*.rb', '*.java', '*.go', '*.cs',  # Backend code
            '*.sql',  # Database scripts
            '*.html', '*.css', '*.scss', '*.jsx', '*.tsx',  # Frontend code
            'Dockerfile', 'docker-compose.yml',  # Docker files
            '*.conf', '*.ini', '*.yml', '*.yaml',  # Configuration files
            '*.c', '*.cpp', '*.h', '*.hpp',  # C/C++ files
            '*.rs',  # Rust files
            '*.scala',  # Scala files
            '*.kt',  # Kotlin files
            '*.swift'  # Swift files
        ]

        return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns_to_analyze)

    def analyze_codebase_performance(self):
        """
        Analyze the performance of all relevant files in a codebase.
        """
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
        
        return self.analyze_performance(file_paths, file_contents)

def main():
    agent = PerformanceAgent()
    results = agent.analyze_codebase_performance()
    
    # Wrap the results in a dictionary with the key "PERFORMANCE_ANALYSIS"
    output = {"PERFORMANCE_ANALYSIS": results}
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()