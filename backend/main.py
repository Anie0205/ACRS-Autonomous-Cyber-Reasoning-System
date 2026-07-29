from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from detector.ast_engine import analyze_code_ast
from patcher.llm_patcher import generate_patch

app = FastAPI(title="ACRS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

# --- Health Check Endpoints (Fixes the 404 Error) ---
@app.get("/")
@app.get("/api/status")
def health_check():
    return {"status": "ok", "message": "ACRS Backend is online"}

# --- Security Scan & Patch Endpoint ---
@app.post("/api/analyze")
def analyze_code(request: CodeRequest):
    # 1. Run deterministic AST check
    vulnerabilities = analyze_code_ast(request.code)
    
    # 2. If safe, return early
    if not vulnerabilities or "error" in vulnerabilities[0]:
        return {
            "status": "safe", 
            "vulnerabilities": vulnerabilities, 
            "patch": None
        }
    
    # 3. If vulnerable, trigger Gemini to patch the first vulnerability found
    target_vuln = vulnerabilities[0]
    patch_data = generate_patch(request.code, target_vuln)
    
    return {
        "status": "vulnerable",
        "vulnerabilities": vulnerabilities,
        "patch": patch_data
    }
