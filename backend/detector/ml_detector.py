import joblib
import os
import numpy as np

class MLDetector:
    """
    ML-based vulnerability detector using TF-IDF + SVM.
    Returns:
        label (int): 1 = vulnerable, 0 = safe
        confidence (float): probability-like score from decision function
    """

    def __init__(self, model_dir="models"):
        self.model_path = os.path.join(model_dir, "svm_model.pkl")
        self.vectorizer_path = os.path.join(model_dir, "tfidf_vectorizer.pkl")

        self.model = joblib.load(self.model_path)
        self.vectorizer = joblib.load(self.vectorizer_path)

    def predict(self, code: str):
        vect = self.vectorizer.transform([code])
        
        # SVM decision function returns distance from hyperplane
        score_raw = self.model.decision_function(vect)[0]

        # Convert to probability-like value
        confidence = float(1 / (1 + np.exp(-score_raw)))

        label = int(self.model.predict(vect)[0])

        return label, confidence
