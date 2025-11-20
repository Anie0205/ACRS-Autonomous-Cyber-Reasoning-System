from acrs.pipeline.acrs import ACRSPipeline

pipeline = ACRSPipeline()

code = """
user = input()
eval(user)
"""

result = pipeline.process(code)

print("\n===== ACRS OUTPUT =====")
print("Detected:", result["detected"])
print("Vulnerability:", result["vulnerability_type"])
print("Patched Code:\n", result["patched_code"])
print("Validated Patch:", result["validated"])
print("========================\n")
