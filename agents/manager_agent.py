import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from architecture_agent import ArchitectureAgent
from static_agent import StaticAgent
from code_quality_agent import CodeQualityAgent
from dependency_agent import DependencyAgent
from performance_agent import PerformanceAgent

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
            
            return None
        except Exception as e:
            print(f"An error occurred while generating the report: {str(e)}")
            return None

    def update_dashboard(self, report):
        """
        Update the dashboard with the latest report data.
        This method would interact with the GUI to update displayed information.
        
        :param report: The JSON report generated by the manager agent
        """
        # In a real implementation, this would update the GUI
        # For now, we'll save the report to a file in the project root
        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'latest_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {report_path}")

def analyze_codebase():
    """
    Analyze the codebase using all specialized agents and generate a comprehensive report.
    """
    # Set the base path to the root directory of the project
    base_path = os.path.dirname(os.path.abspath(__file__))

    # Initialize all agents
    architecture_agent = ArchitectureAgent()
    static_analysis_agent = StaticAgent()
    code_quality_agent = CodeQualityAgent()
    dependency_agent = DependencyAgent()
    performance_agent = PerformanceAgent()
    manager_agent = ManagerAgent()

    # Perform analyses
    architecture_results = architecture_agent.analyze_codebase_architecture(base_path)
    static_analysis_results = static_analysis_agent.analyze_codebase_static(base_path)
    code_quality_results = code_quality_agent.analyze_codebase_quality(base_path)
    dependency_results = dependency_agent.analyze_codebase_dependencies(base_path)
    performance_results = performance_agent.analyze_codebase_performance(base_path)

    # Combine all results
    agent_outputs = {
        "ARCHITECTURE_ANALYSIS": architecture_results,
        "STATIC_CODE_ANALYSIS": static_analysis_results,
        "CODE_QUALITY_ANALYSIS": code_quality_results,
        "DEPENDENCY_AUDIT": dependency_results,
        "PERFORMANCE_ANALYSIS": performance_results
    }

    # Generate comprehensive report
    report = manager_agent.generate_report(agent_outputs)

    if report:
        manager_agent.update_dashboard(report)
    else:
        print("Failed to generate the report.")

def main():
    analyze_codebase()

if __name__ == "__main__":
    main()