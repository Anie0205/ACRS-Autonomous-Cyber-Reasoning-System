import time
import textwrap
from acrs.detector.ml_detector import MLDetector
from acrs.patcher.rules import apply_patch_rules
from acrs.patcher.patcher import generate_patch
from acrs.patcher.patch_ranker import PatchRanker
from acrs.validator.validator import Validator

class ACRSPipeline:
    def __init__(self, ml_model_path="models", vectorizer_path="models", max_iterations=5, save_patches=True):
        self.detector = MLDetector(model_dir=ml_model_path)
        self.rank = PatchRanker()
        self.validator = Validator()

    def log(self, msg: str):
        t = time.strftime("%H:%M:%S")
        print(f"[{t}] {msg}")

    def run(self, code: str):
        return self.process(code)

    def process(self, code: str):
        self.log("Starting ACRS pipeline...")
        
        # [NEW] Pre-processing: Dedent code to fix copy-paste errors
        try:
            clean_code = textwrap.dedent(code)
        except:
            clean_code = code

        # 1. ML Detection
        ml_label, ml_conf = self.detector.predict(clean_code)
        
        # 2. Rule-based Detection
        rule_result = apply_patch_rules(clean_code)
        vuln_type = rule_result["vulnerability_type"]
        rule_patches = rule_result.get("patches", [])
        
        detected = (ml_label == 1) or (vuln_type != "none")

        # Whitelist
        if any(x in clean_code for x in ["safe_eval", "html.escape", "@login_required"]):
            self.log("Safety wrapper/logic detected. Overriding to SAFE.")
            detected = False

        self.log(f"Detection: {detected} | Type: {vuln_type}")

        # 3. Patch Generation
        best_patch = clean_code
        
        if detected:
            self.log("Attempting AST Patch...")
            ast_patch = generate_patch(clean_code)
            
            # SELECTION LOGIC:
            # 1. If AST worked (changed code), use it.
            if ast_patch.replace(" ", "") != clean_code.replace(" ", ""):
                best_patch = ast_patch
            # 2. If AST failed (SyntaxError?), try Regex Fallback from Rules
            elif rule_patches and rule_patches[0] != clean_code:
                self.log("AST failed. Applying Regex Fallback.")
                best_patch = rule_patches[0]
            else:
                self.log("No patch could be generated.")

        # 4. Validation
        is_valid = self.validator.validate(best_patch)

        return {
            "success": is_valid,
            "detected": detected,
            "ml_confidence": ml_conf,
            "vulnerability_type": vuln_type,
            "patch_score": 1.0 if is_valid else 0.0,
            "patched_code": best_patch,
            "validated": is_valid,
        }