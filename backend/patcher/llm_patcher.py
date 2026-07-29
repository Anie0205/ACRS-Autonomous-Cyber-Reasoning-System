import os
import json
from google import genai
from google.genai import types

def generate_patch(source_code: str, vulnerability: dict) -> dict:
    # Requires GEMINI_API_KEY to be set in your Render environment variables
    client = genai.Client()
    
    prompt = f"""
    You are an expert Security Engineer. Fix the vulnerability in this Python code.
    
    Vuln Details: Sink: {vulnerability.get('sink')}, Var: {vulnerability.get('tainted_var')}
    
    Code:
    ```python
    {source_code}
    ```
    
    Return ONLY valid JSON with this structure:
    {{
        "explanation": "Brief risk explanation",
        "fix_summary": "How it was fixed",
        "patched_code": "The full secure code"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        return json.loads(response.text)
    except Exception as e:
        return {
            "explanation": "Error reaching LLM.",
            "fix_summary": str(e),
            "patched_code": source_code
        }
