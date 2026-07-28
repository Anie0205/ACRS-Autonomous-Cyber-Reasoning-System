import os
import subprocess
import tempfile
import shutil
from typing import Dict, Any

class ValidationEngine:
    """
    Executes and validates patched code in an isolated temporary environment.
    Ensures that the LLM-generated patch does not introduce regressions or syntax errors.
    """
    
    def __init__(self, original_test_dir: str):
        # Path to the target repository's test suite
        self.original_test_dir = original_test_dir

    def validate_patch(self, target_filename: str, patched_code: str) -> Dict[str, Any]:
        """
        Creates a sandbox, applies the patch, and runs the test suite.
        """
        # Create a temporary directory to act as the sandbox
        with tempfile.TemporaryDirectory() as sandbox_dir:
            try:
                # 1. Copy the existing test suite to the sandbox
                sandbox_test_dir = os.path.join(sandbox_dir, "tests")
                shutil.copytree(self.original_test_dir, sandbox_test_dir, dirs_exist_ok=True)
                
                # 2. Write the LLM-patched code to the target file in the sandbox
                target_path = os.path.join(sandbox_dir, target_filename)
                
                # Ensure directory structure exists in the sandbox
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                
                with open(target_path, 'w') as f:
                    f.write(patched_code)
                    
                # 3. Execute Pytest in the sandbox environment
                result = subprocess.run(
                    ['pytest', 'tests/'],
                    cwd=sandbox_dir,
                    capture_output=True,
                    text=True,
                    timeout=30 # Prevent infinite loops from bad LLM code
                )
                
                # 4. Evaluate the results
                if result.returncode == 0:
                    return {
                        "success": True,
                        "message": "Patch passed all tests. Ready for PR.",
                        "pytest_output": result.stdout
                    }
                else:
                    return {
                        "success": False,
                        "message": "Patch failed regression tests.",
                        "pytest_output": result.stdout,
                        "pytest_error": result.stderr
                    }
                    
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "message": "Test execution timed out. The patch may have introduced an infinite loop."
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Sandbox error: {str(e)}"
                }

# --- Example Usage ---
# if __name__ == "__main__":
#     validator = ValidationEngine(original_test_dir="./tests")
#     result = validator.validate_patch("app/routes.py", "print('patched code')")
#     print(result)
