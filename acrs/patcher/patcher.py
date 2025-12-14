import ast
import re

class SecureTransformer(ast.NodeTransformer):
    def __init__(self):
        self.modified = False

    def visit_Call(self, node):
        # Fix: eval(x) -> ast.literal_eval(x)
        if isinstance(node.func, ast.Name) and node.func.id == "eval":
            self.modified = True
            new_node = ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id="ast", ctx=ast.Load()),
                    attr="literal_eval",
                    ctx=ast.Load()
                ),
                args=node.args,
                keywords=node.keywords
            )
            return ast.fix_missing_locations(new_node)

        # Fix: exec(x) -> safe_exec(x)
        if isinstance(node.func, ast.Name) and node.func.id == "exec":
            self.modified = True
            new_node = ast.Call(
                func=ast.Name(id="safe_exec", ctx=ast.Load()),
                args=node.args,
                keywords=node.keywords
            )
            return ast.fix_missing_locations(new_node)

        # Fix: subprocess.Popen/call/run -> shell=False
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ["Popen", "call", "run"]:
                shell_keyword = next((k for k in node.keywords if k.arg == "shell"), None)
                if shell_keyword and isinstance(shell_keyword.value, ast.Constant) and shell_keyword.value.value is True:
                    self.modified = True
                    new_keywords = [k for k in node.keywords if k.arg != "shell"]
                    new_keywords.append(ast.keyword(arg="shell", value=ast.Constant(value=False)))
                    node.keywords = new_keywords
                    return node

        return self.generic_visit(node)

def apply_regex_patches(code: str) -> tuple[str, bool]:
    modified = False
    
    # Fix: os.system("cmd " + user) -> subprocess.run([...])
    if "os.system(" in code:
        new_code = re.sub(
            r"os\.system\((.*?)\)",
            r"subprocess.run(\1, shell=False)",
            code
        )
        if new_code != code:
            code = new_code
            modified = True

    # Fix: SQL Injection
    if re.search(r"[\"'].*?SELECT.*?[\"']\s*\+\s*\w+", code, re.IGNORECASE):
        new_code = re.sub(
            r"([\"'].*?)\s*\+\s*(\w+)",
            r"safe_sql(\1, \2)",
            code
        )
        if new_code != code:
            code = new_code
            modified = True

    # Fix: Path Traversal (open calls with concatenation)
    if re.search(r"open\s*\([^)]*\+", code):
        new_code = re.sub(
            r"open\s*\(([^)]*)\)",
            r"safe_open(\1)",
            code
        )
        if new_code != code:
            code = new_code
            modified = True

    return code, modified

def generate_patch(original_code: str) -> str:
    try:
        tree = ast.parse(original_code)
    except SyntaxError:
        return original_code

    transformer = SecureTransformer()
    patched_tree = transformer.visit(tree)
    ast.fix_missing_locations(patched_tree)
    ast_modified = transformer.modified
    
    if ast_modified:
        # Uses built-in unparse (Python 3.9+)
        patched_code = ast.unparse(patched_tree)
    else:
        patched_code = original_code

    patched_code, regex_modified = apply_regex_patches(patched_code)

    if not ast_modified and not regex_modified:
        return original_code

    # --- Dependency Injection ---
    if "ast.literal_eval" in patched_code and "import ast" not in patched_code:
        patched_code = "import ast\n" + patched_code

    if "subprocess" in patched_code and "import subprocess" not in patched_code:
        patched_code = "import subprocess\n" + patched_code

    # --- Helper Injection ---
    
    # safe_exec
    if "safe_exec(" in patched_code and "def safe_exec" not in patched_code:
        helper = """
def safe_exec(code, globals=None, locals=None):
    import ast
    try:
        ast.parse(code)
        exec(code, globals if globals else {}, locals if locals else {})
    except Exception as e:
        print(f"Blocked execution: {e}")
"""
        patched_code = helper + "\n" + patched_code

    # safe_sql
    if "safe_sql(" in patched_code and "def safe_sql" not in patched_code:
        sql_helper = """
def safe_sql(query_part, input_val):
    sanitized = input_val.replace("'", "''")
    return query_part + sanitized
"""
        patched_code = sql_helper + "\n" + patched_code

    # safe_open
    if "safe_open(" in patched_code and "def safe_open" not in patched_code:
        open_helper = """
def safe_open(path, mode="r"):
    import os
    # Basic path traversal prevention
    if ".." in path:
        raise ValueError("Path traversal detected")
    return open(path, mode)
"""
        patched_code = open_helper + "\n" + patched_code

    return patched_code