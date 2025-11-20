class PatchRanker:
    """
    Scores patches based on simple heuristics:
      - shorter patches preferred
      - lower risk operations preferred
    Returns a float score.
    """

    def __init__(self):
        pass

    def score(self, patch: str) -> float:
        """
        Higher is better. Simple heuristic:
        - Penalize very long patches
        - Reward patches that remove dangerous calls
        """
        base = 1.0

        if "eval(" in patch or "exec(" in patch:
            base -= 0.5

        penalty = min(len(patch) / 500.0, 1.0)
        final_score = base - penalty

        return float(final_score)

    def rank(self, patches: list) -> float:
        """
        patches: list of candidate patch strings
        Returns the best patch's score.
        """
        if not patches:
            return 0.0

        scored = [(self.score(p), p) for p in patches]
        scored.sort(key=lambda x: x[0], reverse=True)

        # Return SCORE (NOT code)
        return scored[0][0]
