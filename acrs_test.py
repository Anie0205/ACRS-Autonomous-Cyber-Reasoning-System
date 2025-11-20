# acrs_test.py
from acrs.pipeline.acrs import ACRSPipeline
import textwrap
import sys

pipeline = ACRSPipeline()

TEST_CASES = [
    {
        "name": "Eval Injection",
        "code": """
            user = input()
            eval(user)
        """,
        "expect_detected": True,
        "expect_vuln": "eval_usage",
    },
    {
        "name": "Exec Injection",
        "code": """
            data = input()
            exec(data)
        """,
        "expect_detected": True,
        "expect_vuln": "exec_usage",
    },
    {
        "name": "SQL Injection",
        "code": """
            import sqlite3
            user = input()
            query = "SELECT * FROM users WHERE name = '" + user + "'"
            cursor.execute(query)
        """,
        "expect_detected": True,
        "expect_vuln": "sql_injection",
    },
    {
        "name": "Path Traversal",
        "code": """
            filename = input()
            open("/home/data/" + filename, "r")
        """,
        "expect_detected": True,
        "expect_vuln": "path_traversal",
    },
    {
        "name": "Safe Code (should NOT detect)",
        "code": """
            print("Hello")
            x = 5 + 2
        """,
        "expect_detected": False,
        "expect_vuln": "none",
    },
    {
        "name": "Already Patched Code",
        "code": """
            user = input()
            safe_eval(user)
        """,
        "expect_detected": False,
        "expect_vuln": "none",
    },
]


def run_test(index, test):
    print(f"\n=== TEST {index+1}: {test['name']} ===")
    code = textwrap.dedent(test["code"])

    result = pipeline.process(code)

    detected = result["detected"]
    vuln = result["vulnerability_type"]
    patched = result["patched_code"]
    validated = result["validated"]

    print("Detected:", detected)
    print("Vulnerability Type:", vuln)
    print("Patched Code:\n", patched)
    print("Patch Validated:", validated)

    # Assertions
    ok = True
    if detected != test["expect_detected"]:
        print("❌ Detection mismatch!")
        ok = False

    if vuln != test["expect_vuln"]:
        print("❌ Vulnerability type mismatch!")
        ok = False

    if detected:
        if not patched or patched.strip() == code.strip():
            print("❌ Patch was not applied correctly!")
            ok = False

    if detected and not validated:
        print("❌ Patch validator failed!")
        ok = False

    if not detected and patched and patched != code:
        print("❌ Safe code modified unnecessarily!")
        ok = False

    print("✔ TEST PASSED" if ok else "❌ TEST FAILED")
    return ok


if __name__ == "__main__":
    print("\n--------------------------")
    print("   ACRS FULL TEST SUITE   ")
    print("--------------------------")

    results = []
    for i, t in enumerate(TEST_CASES):
        results.append(run_test(i, t))

    print("\n==========================")
    print("   TEST SUITE SUMMARY     ")
    print("==========================")

    total = len(results)
    passed = results.count(True)

    print(f"Passed: {passed}/{total}")
    if passed == total:
        print("🎉 ALL TESTS PASSED. ACRS IS FULLY FUNCTIONAL.")
    else:
        print("⚠ SOME TESTS FAILED. PLEASE CHECK ABOVE OUTPUT.")
        sys.exit(1)
