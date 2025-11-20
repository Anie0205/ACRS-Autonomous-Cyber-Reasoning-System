# rules.py
import re

def apply_patch_rules(code: str) -> dict:
    """
    Rule-based vulnerability detector and patcher.

    Returns:
        {
            "vulnerability_type": str,
            "severity": str,
            "patches": [patched_code1, ...]
        }
    """
    patches = []
    vuln_type = "none"
    severity = "none"

    # ============================================================
    # RULE 1: Dangerous eval() → eval_usage
    # ============================================================
    if re.search(r"\beval\s*\(", code):
        vuln_type = "eval_usage"
        severity = "high"
        patched = re.sub(r"\beval\s*\(", "safe_eval(", code)
        patches.append(patched)

    # ============================================================
    # RULE 2: Dangerous exec() → exec_usage
    # ============================================================
    if re.search(r"\bexec\s*\(", code):
        vuln_type = "exec_usage"
        severity = "high"
        patched = re.sub(r"\bexec\s*\(", "safe_exec(", code)
        patches.append(patched)

    # ============================================================
    # RULE 3: SQL Injection → sql_injection
    # Detect concatenation of strings in SQL statements
    # ============================================================
    sql_concat_pattern = r"(SELECT|INSERT|UPDATE|DELETE)[^;]*\+"
    if re.search(sql_concat_pattern, code, flags=re.IGNORECASE):
        vuln_type = "sql_injection"
        severity = "critical"

        # Replace simple "query = '...' + var" with safe_sql('...', var)
        patched = re.sub(
            r"\"([^\"]*)\"\s*\+\s*(\w+)",
            r"safe_sql(\"\1\", \2)",
            code
        )
        patches.append(patched)

    # ============================================================
    # RULE 4: Path Traversal → path_traversal
    # Detect open() with string concatenation
    # ============================================================
    if re.search(r"open\s*\([^)]*\+", code):
        vuln_type = "path_traversal"
        severity = "high"
        patched = re.sub(
            r"open\s*\(([^)]*)\)",
            r"safe_open(\1)",
            code
        )
        patches.append(patched)

    # ============================================================
    # RULE 5: Command Injection → command_injection
    # ============================================================
    if "os.system(" in code:
        vuln_type = "command_injection"
        severity = "critical"
        patched = re.sub(r"os.system\s*\(", "safe_exec_shell(", code)
        patches.append(patched)

    # ============================================================
    # RULE 6: Unsafe file open → unsafe_file_open
    # open() without mode argument
    # ============================================================
    open_pattern = r"open\(\s*[^,]+?\s*\)"
    if re.search(open_pattern, code):
        vuln_type = "unsafe_file_open"
        severity = "medium"
        patched = re.sub(open_pattern, r"open(\g<0>, 'r')", code)
        patches.append(patched)

    return {
        "vulnerability_type": vuln_type,
        "severity": severity,
        "patches": patches,
    }
