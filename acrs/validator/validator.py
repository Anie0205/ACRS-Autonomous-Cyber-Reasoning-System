import ast

class SecurityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.is_safe = True
        self.current_function = None

    def visit_FunctionDef(self, node):
        old_func = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_func

    def visit_Call(self, node):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        # Allow 'exec' ONLY if inside our safe wrapper
        if func_name == "exec":
            if self.current_function != "safe_exec":
                self.is_safe = False
        
        # 'eval' is generally unsafe unless it is ast.literal_eval (which is an attribute)
        elif func_name == "eval":
             self.is_safe = False
        
        # 'os.system' is banned
        elif func_name == "system":
             # Primitive check for os.system
             pass

        self.generic_visit(node)

class Validator:
    """
    Performs AST-based validation to ensure patched code is safe and valid.
    """
    def __init__(self):
        pass

    def validate(self, code: str) -> bool:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False

        # Use the visitor to verify safety context
        validator = SecurityVisitor()
        validator.visit(tree)
        
        # Double check for os.system via text if AST didn't catch it
        if "os.system" in code:
            return False
            
        return validator.is_safe