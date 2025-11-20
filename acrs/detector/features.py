import re
import ast

class CodeTokenizer:
    """
    Tokenizes Python code into meaningful tokens for ML models.
    Uses:
        - AST parsing (preferred)
        - Regex fallback (when code is syntactically broken)
    """

    @staticmethod
    def ast_tokenize(code: str):
        """Tokenize using AST (structural tokens)."""
        try:
            tree = ast.parse(code)
        except Exception:
            return None

        tokens = []

        for node in ast.walk(tree):
            node_type = type(node).__name__
            tokens.append(node_type)

            # Capture function names & variable identifiers
            if isinstance(node, ast.Name):
                tokens.append(f"NAME_{node.id}")
            if isinstance(node, ast.Attribute):
                tokens.append(f"ATTR_{node.attr}")
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    tokens.append(f"CALL_{node.func.id}")
                elif isinstance(node.func, ast.Attribute):
                    tokens.append(f"CALL_{node.func.attr}")

        return tokens

    @staticmethod
    def regex_tokenize(code: str):
        """Fallback tokenizer using regex word extraction."""
        tokens = re.findall(r"[A-Za-z_]+|\d+|==|!=|<=|>=|[-+*/%()]", code)
        return tokens

    @staticmethod
    def tokenize(code: str):
        """Main tokenization: AST → regex fallback."""
        ast_tokens = CodeTokenizer.ast_tokenize(code)
        if ast_tokens:
            return ast_tokens
        return CodeTokenizer.regex_tokenize(code)


def preprocess_code(code: str) -> str:
    """
    Converts code into a single string of tokens,
    ready for TF-IDF vectorization.
    """
    tokens = CodeTokenizer.tokenize(code)
    token_string = " ".join(tokens)
    return token_string
