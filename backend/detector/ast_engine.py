import ast
from typing import List, Dict, Any

class TaintVisitor(ast.NodeVisitor):
    SOURCES = {'input', 'request.args.get', 'request.form.get', 'request.get_json'}
    SINKS = {'eval', 'exec', 'os.system', 'subprocess.Popen', 'subprocess.run', 'sqlite3.connect'}

    def __init__(self):
        self.tainted_vars = set()
        self.vulnerabilities: List[Dict[str, Any]] = []

    def _is_tainted_expr(self, node: ast.AST) -> bool:
        """Recursively checks if an AST node originates from an untrusted source or tainted variable."""
        if isinstance(node, ast.Name):
            return node.id in self.tainted_vars
        elif isinstance(node, ast.Call):
            func_name = self._get_func_name(node.func)
            if func_name in self.SOURCES:
                return True
            return any(self._is_tainted_expr(arg) for arg in node.args)
        elif isinstance(node, ast.BinOp):
            return self._is_tainted_expr(node.left) or self._is_tainted_expr(node.right)
        elif isinstance(node, ast.JoinedStr):
            for val in node.values:
                if isinstance(val, ast.FormattedValue) and self._is_tainted_expr(val.value):
                    return True
        return False

    def visit_Assign(self, node: ast.Assign):
        if self._is_tainted_expr(node.value):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.tainted_vars.add(target.id)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        func_name = self._get_func_name(node.func)
        if func_name in self.SINKS:
            for arg in node.args:
                if self._is_tainted_expr(arg):
                    tainted_var_name = arg.id if isinstance(arg, ast.Name) else "inline_expression"
                    self.vulnerabilities.append({
                        "line": getattr(node, 'lineno', 1),
                        "sink": func_name,
                        "tainted_var": tainted_var_name,
                        "cwe": "CWE-95: Eval Injection" if func_name in {'eval', 'exec'} else "CWE-78: OS Command Injection"
                    })
                    break
        self.generic_visit(node)

    def _get_func_name(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            val = self._get_func_name(node.value)
            return f"{val}.{node.attr}" if val else node.attr
        return ""

def analyze_code_ast(source_code: str) -> List[Dict[str, Any]]:
    try:
        tree = ast.parse(source_code)
        visitor = TaintVisitor()
        visitor.visit(tree)
        return visitor.vulnerabilities
    except SyntaxError as e:
        return [{"error": f"Syntax error during AST parsing: {str(e)}"}]