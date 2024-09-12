import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from agents.architecture_agent import ArchitectureAgent
from agents.static_agent import StaticAgent
from agents.code_quality_agent import CodeQualityAgent
from agents.dependency_agent import DependencyAgent
from agents.performance_agent import PerformanceAgent

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load the system prompt from .env
MANAGER_SYS_PROMPT = os.getenv("MANAGER_SYS_PROMPT")

class ManagerAgent:
    def __init__(self):
        self.client = client
        self.system_prompt = MANAGER_SYS_PROMPT

    def generate_report(self, agent_outputs):
        """
        Generate a comprehensive report based on the outputs of specialized agents.
        
        :param agent_outputs: A dictionary containing the outputs from each specialized agent
        :return: A JSON object containing the aggregated report
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "generate_comprehensive_report",
                    "description": "Generate a comprehensive security and quality report based on various analyses",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "overallSummary": {"type": "string"},
                            "securityAssessment": {
                                "type": "object",
                                "properties": {
                                    "overallRisk": {"type": "string", "enum": ["Low", "Medium", "High", "Critical"]},
                                    "keyVulnerabilities": {"type": "array", "items": {"type": "string"}},
                                    "recommendations": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "codeQualityAssessment": {
                                "type": "object",
                                "properties": {
                                    "overallQuality": {"type": "string", "enum": ["Poor", "Fair", "Good", "Excellent"]},
                                    "keyIssues": {"type": "array", "items": {"type": "string"}},
                                    "recommendations": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "performanceAssessment": {
                                "type": "object",
                                "properties": {
                                    "overallPerformance": {"type": "string", "enum": ["Poor", "Fair", "Good", "Excellent"]},
                                    "keyBottlenecks": {"type": "array", "items": {"type": "string"}},
                                    "recommendations": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "architectureAssessment": {
                                "type": "object",
                                "properties": {
                                    "overallArchitecture": {"type": "string", "enum": ["Poor", "Fair", "Good", "Excellent"]},
                                    "keyStrengths": {"type": "array", "items": {"type": "string"}},
                                    "keyWeaknesses": {"type": "array", "items": {"type": "string"}},
                                    "recommendations": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "dependencyAssessment": {
                                "type": "object",
                                "properties": {
                                    "overallDependencyHealth": {"type": "string", "enum": ["Poor", "Fair", "Good", "Excellent"]},
                                    "outdatedDependencies": {"type": "integer"},
                                    "vulnerableDependencies": {"type": "integer"},
                                    "recommendations": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "prioritizedActionItems": {"type": "array", "items": {"type": "string"}},
                            "overallProjectHealth": {"type": "string", "enum": ["Critical", "At Risk", "Stable", "Healthy"]}
                        },
                        "required": ["overallSummary", "securityAssessment", "codeQualityAssessment", "performanceAssessment", "architectureAssessment", "dependencyAssessment", "prioritizedActionItems", "overallProjectHealth"]
                    }
                }
            }
        ]

        input_content = json.dumps(agent_outputs, indent=2)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Analyze the following outputs from our specialized agents and generate a comprehensive report:\n\n{input_content}"}
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice={"type": "function", "function": {"name": "generate_comprehensive_report"}}
            )
            
            if response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                if tool_call.function.name == "generate_comprehensive_report":
                    return json.loads(tool_call.function.arguments)
            
            return {"error": "Failed to generate the report."}
        except Exception as e:
            return {"error": f"An error occurred while generating the report: {str(e)}"}

def analyze_codebase():
    """
    Analyze the codebase using all specialized agents and generate a comprehensive report.
    """
    # Initialize all agents
    architecture_agent = ArchitectureAgent()
    static_analysis_agent = StaticAgent()
    code_quality_agent = CodeQualityAgent()
    dependency_agent = DependencyAgent()
    performance_agent = PerformanceAgent()
    manager_agent = ManagerAgent()

    # Perform analyses
    architecture_results = architecture_agent.analyze_codebase_architecture()
    static_analysis_results = static_analysis_agent.analyze_codebase_static()
    code_quality_results = code_quality_agent.analyze_codebase_quality()
    dependency_results = dependency_agent.analyze_codebase_dependencies()
    performance_results = performance_agent.analyze_codebase_performance()

    # Combine all results
    agent_outputs = {
        "ARCHITECTURE_ANALYSIS": architecture_results,
        "STATIC_CODE_ANALYSIS": static_analysis_results,
        "CODE_QUALITY_ANALYSIS": code_quality_results,
        "DEPENDENCY_AUDIT": dependency_results,
        "PERFORMANCE_ANALYSIS": performance_results
    }

    # Generate comprehensive report
    return manager_agent.generate_report(agent_outputs)

def main():
    report = analyze_codebase()
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()