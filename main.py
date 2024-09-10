import os
from dotenv import load_dotenv
from static_agent import analyze_codebase

# Load environment variables
load_dotenv()

def main(base_path: str):
    """
    Main function to analyze the codebase.
    """
    try:
        if not os.path.isdir(base_path):
            raise ValueError("Invalid base path")
        
        analysis_results = analyze_codebase(base_path)
        return {"results": analysis_results}
    except Exception as e:
        return {"error": f"An error occurred during analysis: {str(e)}"}

if __name__ == "__main__":
    # This block is for testing purposes
    base_path = "."  # Current directory
    results = main(base_path)
    print(results)