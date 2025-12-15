import re

def apply_patch_rules(code: str) -> dict:
    patches = []
    vuln_type = "none"
    severity = "low"

    # ============================================================
    # 1. WEB: Reflected XSS (Broader Detection)
    # ============================================================
    # OLD STRICT RULE: r"return\s+f['\"].*?<[a-zA-Z]+>.*?\{.*?\}"
    # NEW BROAD RULE: Detects f" ... <h1> ... {var} ... " anywhere.
    # We look for: f + quote + anything + <tag> + anything + {var} + anything + quote
    xss_pattern = r"f['\"](?:[^'\"{}]*<[a-zA-Z]+>[^'\"{}]*\{[^}]+\}|[^'\"{}]*\{[^}]+\}[^'\"{}]*<[a-zA-Z]+>)"
    
    if re.search(xss_pattern, code, re.IGNORECASE):
        vuln_type = "reflected_xss"
        severity = "high"
        
        # Fallback Regex Patch (if AST fails)
        def xss_replacer(match):
            content = match.group(0)
            # Wrap {var} in {html.escape(var)} unless it's already safe
            # Regex lookbehind is hard here, so we just iterate matches
            return re.sub(r"\{([a-zA-Z0-9_]+)\}", r"{html.escape(\1)}", content)

        patched = re.sub(xss_pattern, xss_replacer, code)
        if "html.escape" in patched and "import html" not in patched:
            patched = "import html\n" + patched
            
        patches.append(patched)

    # ============================================================
    # 2. WEB: Broken Access Control
    # ============================================================
    if re.search(r"@\w+\.route\s*\(\s*['\"]/admin", code):
        if not re.search(r"@\s*(login_required|jwt_required|auth_required)", code):
            vuln_type = "broken_access_control"
            severity = "critical"
            patches.append(re.sub(
                r"(@\w+\.route\s*\(\s*['\"]/admin.*?\))", 
                r"\1\n# [ACRS] CRITICAL: Missing Access Control! Add @login_required.", 
                code
            ))

    # ============================================================
    # 3. WEB: CORS Misconfiguration
    # ============================================================
    if re.search(r"CORS\s*\(\s*\w+\s*(?!\s*,.*?resources)", code):
        vuln_type = "cors_misconfiguration"
        severity = "medium"
        patches.append(code)

    # ============================================================
    # 4. SYSTEM: Existing Rules
    # ============================================================
    sql_keywords = r"(SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)"
    if re.search(fr'f[\'"].*?{sql_keywords}.*?\{{.*?\}}', code, re.IGNORECASE | re.DOTALL):
        vuln_type = "sql_injection"
        severity = "critical"
        patches.append(code)
    
    if re.search(r"\beval\s*\(", code):
        vuln_type = "eval_usage"
        patches.append(re.sub(r"\beval\s*\(", "ast.literal_eval(", code))
    
    if re.search(r"open\s*\(\s*(?!['\"])[a-zA-Z_]", code):
        vuln_type = "path_traversal"
        severity = "high"
        patches.append(code)

    return {
        "vulnerability_type": vuln_type,
        "severity": severity,
        "patches": patches,
    }