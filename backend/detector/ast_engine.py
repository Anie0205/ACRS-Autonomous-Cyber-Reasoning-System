import ast
from typing import List, Dict, Any

class TaintVisitor(ast.NodeVisitor):
    """
    AST Visitor that tracks variable assignments from untrusted SOURCES 
    and checks if they reach dangerous SINKS without sanitization.
    """
    SOURCES = {'input', 'request.args.get', 'request.form.get'}
    SINKS = {'eval', 'exec', 'os.system', 'subprocess.Popen', 'sqlite3.connect'}

    def __init__(self):
        self.tainted_vars = set()
        self.vulnerabilities: List[Dict[str, Any]] = []

    def visit_Assign(self, node: ast.Assign):
        # Check if the right side of assignment comes from a tainted source
        if isinstance(node.value, ast.Call):
            func_name = self._get_func_name(node.value.func)
            if func_name in self.SOURCES:
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.tainted_vars.add(target.id)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_name = self._get_func_name(node.func)
        
        # Check if a dangerous sink is called with a tainted variable
        if func_name in self.SINKS:
            for arg in node.args:
                if isinstance(arg, ast.Name) and arg.id in self.tainted_vars:
                    self.vulnerabilities.append({
                        "line": node.lineno,
                        "sink": func_name,
                        "tainted_var": arg.id,
                        "cwe": "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code ('Eval Injection')" if func_name in {'eval', 'exec'} else "CWE-78: OS Command Injection"
                    })
        self.generic_visit(node)

    def _get_func_name(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_func_name(node.value)}.{node.attr}"
        return ""

def analyze_code_ast(source_code: str) -> List[Dict[str, Any]]:
    """Parses Python source code and identifies taint-based security vulnerabilities."""
    try:
        tree = ast.parse(source_code)
        visitor = TaintVisitor()
        visitor.visit(tree)
        return visitor.vulnerabilities
    except SyntaxError as e:
        return [{"error": f"Syntax error during AST parsing: {str(e)}"}]
