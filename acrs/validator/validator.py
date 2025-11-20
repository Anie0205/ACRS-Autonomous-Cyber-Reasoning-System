import ast

class Validator:
    """
    Performs AST-based validation to ensure patched code is safe and valid.
    """

    def __init__(self):
        pass

    def validate(self, code: str) -> bool:
        """
        Returns True if code is syntactically valid and contains no dangerous calls.
        """
        # Step 1: AST syntax validation
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False

        # Step 2: Detect any remaining vulnerable patterns
        dangerous_calls = {"eval", "exec", "os.system"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and hasattr(node.func, "id"):
                if node.func.id in dangerous_calls:
                    return False

        return True
