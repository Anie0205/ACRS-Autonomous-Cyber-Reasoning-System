# acrs/validator/test_runner.py

import subprocess
import tempfile
import os
import sys


class TestRunner:
    def __init__(self, timeout=3):
        self.timeout = timeout

    def run(self, code):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
            tmp.write(code.encode())
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                timeout=self.timeout
            )
            return {
                "ok": result.returncode == 0,
                "stdout": result.stdout.decode(),
                "stderr": result.stderr.decode(),
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "Timeout"}
        finally:
            os.unlink(tmp_path)
