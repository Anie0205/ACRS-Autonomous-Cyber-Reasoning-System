import ast
import re

class AdvancedSecureTransformer(ast.NodeTransformer):
    def __init__(self):
        self.modified = False

    def visit_Call(self, node):
        # 1. FIX: CORS
        if isinstance(node.func, ast.Name) and node.func.id == "CORS":
            has_resources = any(k.arg == "resources" for k in node.keywords)
            if not has_resources:
                self.modified = True
                inner_dict = ast.Dict(keys=[ast.Constant(value="origins")], values=[ast.Constant(value="https://trusted.com")])
                outer_dict = ast.Dict(keys=[ast.Constant(value=r"/*")], values=[inner_dict])
                node.keywords.append(ast.keyword(arg="resources", value=outer_dict))
                return ast.fix_missing_locations(node)
        
        # 2. FIX: Eval/Exec/Open
        if isinstance(node.func, ast.Name):
            if node.func.id == "eval":
                self.modified = True
                node.func = ast.Attribute(value=ast.Name(id="ast", ctx=ast.Load()), attr="literal_eval", ctx=ast.Load())
            elif node.func.id == "exec":
                self.modified = True
                node.func.id = "safe_exec"
            elif node.func.id == "open":
                # Check if arg is not a string literal
                if node.args and not (isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)):
                    self.modified = True
                    node.func.id = "safe_open"
            return ast.fix_missing_locations(node)
            
        return self.generic_visit(node)

    def visit_JoinedStr(self, node):
        # 3. FIX: Reflected XSS
        # Check if ANY part of the f-string looks like an HTML tag
        is_html = False
        for part in node.values:
            if isinstance(part, ast.Constant) and isinstance(part.value, str):
                # Loose regex: <tag>
                if re.search(r"<[a-zA-Z0-9]+.*?>", part.value):
                    is_html = True
                    break
        
        if is_html:
            new_values = []
            changes_made = False
            for part in node.values:
                # Wrap {var} -> {html.escape(var)}
                # But check if it is ALREADY wrapped in a function call (like html.escape)
                if isinstance(part, ast.FormattedValue):
                    # Check if value is a Name (var) vs Call (func())
                    if isinstance(part.value, ast.Name):
                        changes_made = True
                        escape_call = ast.Call(
                            func=ast.Attribute(value=ast.Name(id="html", ctx=ast.Load()), attr="escape", ctx=ast.Load()),
                            args=[part.value], keywords=[]
                        )
                        new_values.append(ast.FormattedValue(value=escape_call, conversion=part.conversion, format_spec=part.format_spec))
                    else:
                        new_values.append(part)
                else:
                    new_values.append(part)
            
            if changes_made:
                self.modified = True
                node.values = new_values
                return node

        return self.generic_visit(node)

def generate_patch(original_code: str) -> str:
    try:
        tree = ast.parse(original_code)
    except SyntaxError:
        return original_code

    transformer = AdvancedSecureTransformer()
    patched_tree = transformer.visit(tree)
    ast.fix_missing_locations(patched_tree)
    
    if transformer.modified:
        patched_code = ast.unparse(patched_tree)
    else:
        patched_code = original_code

    if "html.escape" in patched_code and "import html" not in patched_code:
        patched_code = "import html\n" + patched_code
    if "ast.literal_eval" in patched_code and "import ast" not in patched_code:
        patched_code = "import ast\n" + patched_code

    # Inject helpers if needed (safe_exec, safe_open, safe_sql...)
    # (Abbreviated for clarity, assume previous helpers logic is here)
    if "safe_open(" in patched_code and "def safe_open" not in patched_code:
        patched_code = "def safe_open(p, m='r'): \n    if '..' in p: raise ValueError()\n    return open(p, m)\n" + patched_code

    return patched_code