import os
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from .features import preprocess_code


DATA_DIR = "data"
MODEL_PATH = "models/svm_model.pkl"
VEC_PATH = "models/tfidf_vectorizer.pkl"


def load_dataset():
    """
    Loads training data from:
        data/vuln/*.py  → label = 1
        data/safe/*.py  → label = 0
    """
    texts = []
    labels = []

    vuln_dir = os.path.join(DATA_DIR, "vuln")
    safe_dir = os.path.join(DATA_DIR, "safe")

    # Vulnerable samples
    for file in os.listdir(vuln_dir):
        if file.endswith(".py"):
            path = os.path.join(vuln_dir, file)
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
                texts.append(preprocess_code(code))
                labels.append(1)

    # Safe samples
    for file in os.listdir(safe_dir):
        if file.endswith(".py"):
            path = os.path.join(safe_dir, file)
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
                texts.append(preprocess_code(code))
                labels.append(0)

    return texts, labels


def train_model():
    print("[+] Loading dataset...")
    texts, labels = load_dataset()

    print(f"[+] Loaded {len(texts)} training samples.")

    # Train/val split
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )

    print("[+] Initializing TF-IDF + SVM pipeline...")

    vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1
    )

    svm = LinearSVC()

    # Fit vectorizer + model
    print("[+] Training TF-IDF vectorizer...")
    X_train_vec = vectorizer.fit_transform(X_train)

    print("[+] Training SVM classifier...")
    svm.fit(X_train_vec, y_train)

    # Evaluate
    print("[+] Evaluating...")
    X_test_vec = vectorizer.transform(X_test)
    preds = svm.predict(X_test_vec)

    print(classification_report(y_test, preds, digits=4))

    # Save model + vectorizer
    print("[+] Saving model...")
    os.makedirs("models", exist_ok=True)
    joblib.dump(svm, MODEL_PATH)
    joblib.dump(vectorizer, VEC_PATH)

    print(f"[✓] Saved SVM model → {MODEL_PATH}")
    print(f"[✓] Saved TF-IDF vectorizer → {VEC_PATH}")


if __name__ == "__main__":
    train_model()
