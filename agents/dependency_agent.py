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

class DependencyAgent:
    def __init__(self):
        self.client = client
        self.system_prompt = DEPENDENCY_SYS_PROMPT

    def analyze_dependencies(self, file_paths, file_contents):
        """
        Analyze the dependencies of the codebase.
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "report_dependency_analysis",
                    "description": "Report the dependency analysis of the codebase",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "directDependencies": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "version": {"type": "string"},
                                        "latestVersion": {"type": "string"},
                                        "isOutdated": {"type": "boolean"},
                                        "securityVulnerabilities": {"type": "array", "items": {"type": "string"}},
                                        "license": {"type": "string"},
                                        "usageLocations": {"type": "array", "items": {"type": "string"}}
                                    }
                                }
                            },
                            "transitiveDependencies": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "version": {"type": "string"},
                                        "parentDependencies": {"type": "array", "items": {"type": "string"}},
                                        "securityVulnerabilities": {"type": "array", "items": {"type": "string"}}
                                    }
                                }
                            },
                            "dependencyGraphComplexity": {"type": "string"},
                            "outdatedDependenciesCount": {"type": "integer"},
                            "vulnerableDependenciesCount": {"type": "integer"},
                            "licensingIssues": {"type": "array", "items": {"type": "string"}},
                            "unusedDependencies": {"type": "array", "items": {"type": "string"}},
                            "overallDependencyHealth": {"type": "string", "enum": ["Poor", "Fair", "Good", "Excellent"]},
                            "keyRecommendations": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["directDependencies", "overallDependencyHealth", "keyRecommendations"]
                    }
                }
            }
        ]

        # Prepare the content for analysis
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
                return json.loads(tool_call.function.arguments)
        
        return None

    def should_analyze_file(self, file_path):
        """
        Determine if a file should be analyzed based on its extension and name.
        """
        patterns_to_analyze = [
            'package.json', 'requirements.txt', 'Gemfile', 'pom.xml',  # Package managers
            '*.csproj', '*.fsproj', '*.vbproj',  # .NET project files
            'build.gradle', 'build.sbt',  # Java/Scala build files
            'Cargo.toml',  # Rust
            'go.mod',  # Go
            'composer.json',  # PHP
            'Podfile',  # iOS
            'build.gradle.kts',  # Kotlin
            'pubspec.yaml',  # Dart/Flutter
            'project.clj',  # Clojure
            'mix.exs',  # Elixir
            'rebar.config',  # Erlang
            'environment.yml', 'conda-environment.yml',  # Conda environments
            'Pipfile',  # Pipenv
            'pyproject.toml',  # Python packaging
            'yarn.lock', 'package-lock.json', 'npm-shrinkwrap.json'  # Lock files
        ]

        return any(fnmatch.fnmatch(file_path, pattern) for pattern in patterns_to_analyze)

    def analyze_codebase_dependencies(self, base_path):
        """
        Analyze the dependencies of all relevant files in a codebase.
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
        
        return self.analyze_dependencies(file_paths, file_contents)

def main():
    agent = DependencyAgent()
    base_path = "."  # Current directory
    results = agent.analyze_codebase_dependencies(base_path)
    
    # Wrap the results in a dictionary with the key "DEPENDENCY_AUDIT"
    output = {"DEPENDENCY_AUDIT": results}
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()