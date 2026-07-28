import os
import json
from google import genai
from google.genai import types

def generate_patch(source_code: str, vulnerability: dict) -> dict:
    """
    Uses the Gemini API to analyze a vulnerability and generate a verified secure patch.
    Expects GEMINI_API_KEY to be set in the environment variables.
    """
    # Initialize the unified Google GenAI client
    client = genai.Client()
    
    prompt = f"""
    You are an expert Application Security Engineer. You have been provided with 
    a piece of Python code that contains a security vulnerability identified by our AST engine.

    Vulnerability Details:
    - Target Sink: {vulnerability.get('sink')}
    - Tainted Variable: {vulnerability.get('tainted_var')}
    - Line Number: {vulnerability.get('line')}
    - CWE: {vulnerability.get('cwe')}

    Original Source Code:
    ```python
    {source_code}
    ```

    Your task is to remediate this vulnerability. Implement proper sanitization, validation, or 
    use safe alternatives (e.g., `ast.literal_eval` instead of `eval`, or parameterized queries).
    
    Return ONLY a valid JSON object with the following structure:
    {{
        "explanation": "Brief explanation of the risk.",
        "fix_summary": "Brief explanation of how the patch resolves the issue.",
        "patched_code": "The complete, secure Python code."
    }}
    """
    
    try:
        # Using gemini-3.5-flash for sustained frontier performance on coding tasks
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1 # Low temperature for deterministic, safe code generation
            )
        )
        
        # Parse and return the structured JSON payload
        return json.loads(response.text)
        
    except Exception as e:
        return {"error": f"LLM Patch Generation Failed: {str(e)}"}

# --- Example Usage ---
# if __name__ == "__main__":
#     vuln = {"sink": "eval", "tainted_var": "user_input", "line": 2, "cwe": "CWE-95"}
#     code = "user_input = input()\neval(user_input)"
#     print(json.dumps(generate_patch(code, vuln), indent=2))
