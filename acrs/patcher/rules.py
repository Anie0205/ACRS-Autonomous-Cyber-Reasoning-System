"""
rules.py
--------
Full rule-based vulnerability detector producing:
- vulnerability_type
- severity
- patches: [patched_code]
"""

import re

def apply_patch_rules(code: str) -> dict:
    """
    Rule-based vulnerability detector.

    Inputs
    ------
    code : str
        Raw Python code text.

    Returns
    -------
    dict:
        {
            "vulnerability_type": str,
            "patches": [patched_code1, ...]
        }
    """

    patches = []
    vuln_type = "none"

    # ------------------------------------------
    # RULE 1: Dangerous eval()
    # ------------------------------------------
    if "eval(" in code:
        vuln_type = "eval_usage"

        patched = re.sub(r"eval\(", "safe_eval(", code)
        patches.append(patched)

    # ------------------------------------------
    # RULE 2: exec()
    # ------------------------------------------
    if "exec(" in code:
        vuln_type = "exec_usage"

        patched = re.sub(r"exec\(", "safe_exec(", code)
        patches.append(patched)

    # ------------------------------------------
    # RULE 3: os.system()
    # ------------------------------------------
    if "os.system(" in code:
        vuln_type = "command_injection"

        patched = re.sub(r"os.system\(", "safe_exec_shell(", code)
        patches.append(patched)

    # ------------------------------------------
    # RULE 4: open() without mode
    # ------------------------------------------
    open_pattern = r"open\([^,]+\)"
    if re.search(open_pattern, code):
        vuln_type = "unsafe_file_open"

        patched = re.sub(open_pattern, r"open(\g<0>, 'r')", code)
        patches.append(patched)

    # ------------------------------------------
    # If no rules match, return empty patches
    # ------------------------------------------
    return {
        "vulnerability_type": vuln_type,
        "patches": patches,
    }
