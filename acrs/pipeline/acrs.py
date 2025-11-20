import time
from acrs.detector.ml_detector import MLDetector
from acrs.patcher.rules import apply_patch_rules
from acrs.patcher.patch_ranker import PatchRanker
from acrs.validator.validator import Validator


class ACRSPipeline:
    """
    Full Autonomous Cyber Reasoning System (ACRS) pipeline.
    Takes input code → runs ML detection → rule-based vuln detection →
    patch generation → patch ranking → validation → output.
    """

    def __init__(self):
        self.detector = MLDetector()
        self.rank = PatchRanker()
        self.validator = Validator()

    def log(self, msg: str):
        """Simple logger with timestamp."""
        t = time.strftime("%H:%M:%S")
        print(f"[{t}] {msg}")

    def process(self, code: str):
        """
        Entire pipeline:
        1. ML detection (TF-IDF + SVM)
        2. Rule-based vulnerability identification
        3. Patch generation
        4. Patch ranking
        5. Patch validation
        """

        self.log("Starting ACRS pipeline...")

        # ----------------------------
        # Step 1: ML detection
        # ----------------------------
        self.log("Running ML vulnerability detector...")

        ml_label, ml_conf = self.detector.predict(code)

        self.log(f"ML Detector Label: {ml_label} (1=vulnerable)")
        self.log(f"ML Confidence Score: {ml_conf:.4f}")

        detected = bool(ml_label == 1)

        # ----------------------------
        # Step 2: Rule-based detection
        # ----------------------------
        self.log("Running rule-based vulnerability analyzer...")

        rule_result = apply_patch_rules(code)

        vuln_type = rule_result["vulnerability_type"]
        patches = rule_result["patches"]

        self.log(f"Vulnerability Type: {vuln_type}")
        self.log(f"Generated {len(patches)} patch candidates.")

        if not patches:
            self.log("No patch candidates found. Returning original code.")
            return {
                "detected": detected,
                "vulnerability_type": vuln_type,
                "patched_code": code,
                "validated": False,
            }

        # ----------------------------
        # Step 3: Patch ranking
        # ----------------------------
        self.log("Ranking patches using PatchRanker heuristic model...")

        best_score = self.rank.rank(patches)
        best_patch = patches[0]  # list already sorted by rules priority

        self.log(f"Best Patch Score: {best_score:.4f}")

        # ----------------------------
        # Step 4: Static validation
        # ----------------------------
        self.log("Validating patch...")

        is_valid = self.validator.validate(best_patch)

        self.log(f"Patch validation result: {is_valid}")

        # ----------------------------
        # Final response
        # ----------------------------
        result = {
            "detected": detected,
            "ml_confidence": float(ml_conf),
            "vulnerability_type": vuln_type,
            "patched_code": best_patch,
            "validated": is_valid,
        }

        self.log("ACRS pipeline finished.")
        return result
