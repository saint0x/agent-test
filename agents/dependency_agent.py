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
DEPENDENCY_SYS_PROMPT = os.getenv("DEPENDENCY_SYS_PROMPT")

class DependencyAnalysis(BaseModel):
    directDependencies: list[dict]
    transitiveDependencies: list[dict]
    dependencyGraphComplexity: str
    outdatedDependenciesCount: int
    vulnerableDependenciesCount: int
    licensingIssues: list[str]
    unusedDependencies: list[str]
    overallDependencyHealth: str
    keyRecommendations: list[str]

class DependencyAgent:
    def __init__(self):
        self.client = client
        self.system_prompt = DEPENDENCY_SYS_PROMPT

    def analyze_dependencies(self, file_paths, file_contents):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "report_dependency_analysis",
                    "description": "Report the dependency analysis of the codebase",
                    "parameters": DependencyAnalysis.schema(),
                }
            }
        ]

        content = "\n\n".join([f"File: {path}\n\nContent:\n{content}" for path, content in zip(file_paths, file_contents)])

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Analyze the dependencies of the following codebase:\n\n{content}"}
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            if tool_call.function.name == "report_dependency_analysis":
                return DependencyAnalysis.parse_raw(tool_call.function.arguments)

        return None

    def should_analyze_file(self, file_path):
        patterns_to_analyze = [
            'package.json', 'requirements.txt', 'Gemfile', 'pom.xml',
            '*.csproj', '*.fsproj', '*.vbproj',
            'build.gradle', 'build.sbt',
            'Cargo.toml',
            'go.mod',
            'composer.json',
            'Podfile',
            'build.gradle.kts',
            'pubspec.yaml',
            'project.clj',
            'mix.exs',
            'rebar.config',
            'environment.yml', 'conda-environment.yml',
            'Pipfile', 'pyproject.toml',
            'yarn.lock', 'package-lock.json', 'npm-shrinkwrap.json'
        ]

        return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns_to_analyze)

    def analyze_codebase_dependencies(self):
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

        return self.analyze_dependencies(file_paths, file_contents)

def main():
    agent = DependencyAgent()
    results = agent.analyze_codebase_dependencies()
    output = {"DEPENDENCY_AUDIT": results}
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()