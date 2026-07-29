import os
import json
import re
from google import genai
from google.genai import types


def generate_patch(source_code: str, vulnerability: dict) -> dict:
    """
    Uses the Google GenAI SDK (Gemini) to generate a secure,
    context-aware patch for an identified AST vulnerability.
    """
    # 1. Check for API key in environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "explanation": "GEMINI_API_KEY is missing from environment variables.",
            "fix_summary": "Please configure GEMINI_API_KEY in your Render environment variables.",
            "patched_code": source_code
        }

    try:
        # 2. Initialize the Google GenAI Client
        client = genai.Client(api_key=api_key)

        # 3. Construct prompt with AST analysis context
        prompt = f"""You are an expert Application Security Engineer.
Fix the security vulnerability present in this Python code snippet.

Vulnerability Details from AST Taint Analysis:
- Vulnerable Sink: {vulnerability.get('sink')}
- Tainted Variable/Expression: {vulnerability.get('tainted_var')}
- Line Number: {vulnerability.get('line')}
- CWE Standard: {vulnerability.get('cwe')}

Original Source Code:
```python
{source_code}
```

Task Instructions:
1. Provide a secure patch replacing dangerous functions with safe alternatives
   (e.g., ast.literal_eval, parameterized queries, or subprocess with list args).
2. Return ONLY a valid JSON object with the exact keys below:
{{
  "explanation": "Brief explanation of the risk.",
  "fix_summary": "Summary of how the vulnerability was remediated.",
  "patched_code": "The complete secure Python code."
}}
"""

        # 4. Call Gemini with structured JSON output enforced
        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )

        # 5. Clean potential markdown code blocks from LLM response
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = re.sub(r"^```(?:json)?\n?", "", raw_text)
            raw_text = re.sub(r"\n?```$", "", raw_text)
            raw_text = raw_text.strip()

        # 6. Parse structured JSON
        parsed = json.loads(raw_text)
        return {
            "explanation": parsed.get("explanation", "Vulnerability remediated."),
            "fix_summary": parsed.get("fix_summary", "Applied security fix."),
            "patched_code": parsed.get("patched_code", source_code)
        }

    except Exception as e:
        # Graceful fallback on API or parsing failure
        return {
            "explanation": f"LLM Generation Error: {str(e)}",
            "fix_summary": "Failed to generate AI patch automatically.",
            "patched_code": source_code
        }