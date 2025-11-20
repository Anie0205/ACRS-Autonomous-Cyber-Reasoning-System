import os
import joblib
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split

DATA_DIR = "data/"
VULN_DIR = os.path.join(DATA_DIR, "vuln")
SAFE_DIR = os.path.join(DATA_DIR, "safe")

MODEL_DIR = "models/"
MODEL_PATH = os.path.join(MODEL_DIR, "svm_model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")


def load_dataset():
    """Load Python source code files from vuln/ and safe/."""
    samples = []
    labels = []

    print("[INFO] Loading dataset...")

    # Vulnerable files → label = 1
    for fname in os.listdir(VULN_DIR):
        if fname.endswith(".py"):
            with open(os.path.join(VULN_DIR, fname), "r", encoding="utf-8") as f:
                samples.append(f.read())
                labels.append(1)

    # Safe files → label = 0
    for fname in os.listdir(SAFE_DIR):
        if fname.endswith(".py"):
            with open(os.path.join(SAFE_DIR, fname), "r", encoding="utf-8") as f:
                samples.append(f.read())
                labels.append(0)

    print(f"[INFO] Loaded {len(samples)} samples "
          f"({len(os.listdir(VULN_DIR))} vuln, {len(os.listdir(SAFE_DIR))} safe)")

    return samples, labels


def train_detector():
    samples, labels = load_dataset()

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        samples, labels, test_size=0.2, random_state=42, shuffle=True
    )

    # Vectorizer
    print("[INFO] Computing TF-IDF features...")
    vectorizer = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.95,
        token_pattern=r"[A-Za-z_][A-Za-z0-9_]*"
    )

    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Model
    print("[INFO] Training SVM (LinearSVC)...")
    clf = LinearSVC()
    clf.fit(X_train_vec, y_train)

    # Evaluation
    print("\n===== MODEL PERFORMANCE =====")
    preds = clf.predict(X_test_vec)

    print("Accuracy:", accuracy_score(y_test, preds))
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, preds))
    print("\nClassification Report:")
    print(classification_report(y_test, preds))

    # Save artifacts
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    print("\n[INFO] Model saved →", MODEL_PATH)
    print("[INFO] Vectorizer saved →", VECTORIZER_PATH)
    print("\nTraining complete!")


if __name__ == "__main__":
    train_detector()
