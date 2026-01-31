# ACRS: Autonomous Cyber Reasoning System

**ACRS** is a "self-healing" security framework designed to autonomously detect, validate, and patch critical security vulnerabilities in Python web applications (specifically Flask). It combines Machine Learning with AST-based code transformation to close the loop between vulnerability discovery and remediation without human intervention.

---

## 🚀 Key Features

* **Hybrid Detection Engine:**
    * **Machine Learning:** Utilizes a **LinearSVC** model trained on **TF-IDF** vectors (1-2 n-grams) to classify code patterns as Safe or Vulnerable.
    * **Rule-Based Logic:** High-precision Regex patterns to catch specific signatures (e.g., missing `@login_required` on admin routes).
* **Autonomous Patching:**
    * **AST Transformation:** Safely rewrites code structure using Python's `ast` module (e.g., wrapping variables in `html.escape` or replacing `eval` with `ast.literal_eval`).
    * **Regex Fallback:** Applies text-based fixes if AST parsing fails due to syntax errors.
* **Validation Pipeline:** Automatically validates that generated patches are syntactically correct and free of the detected dangerous functions.
* **Synthetic Dataset Generator:** Built-in tool to generate diverse training samples for Broken Access Control vulnerabilities.

---
## Demo
[Click Here](https://acrs-tau.vercel.app/)

---
## 🛡️ Supported Vulnerabilities

| Vulnerability Type | Detection Method | Patching Strategy |
| :--- | :--- | :--- |
| **Broken Access Control** | Regex (Routes starting with `/admin` lacking auth decorators) | **Alerting:** Injects a critical warning comment for developers. |
| **Reflected XSS** | Regex + ML | **Sanitization:** Wraps unsafe variables in `html.escape()`. |
| **Insecure Execution** | Keyword Search (`eval`, `exec`) | **Replacement:** Converts to `ast.literal_eval` or `safe_exec`. |
| **CORS Misconfiguration**| Rule-based | **Restraint:** Restricts wildcard origins to trusted domains. |
| **SQL Injection** | Regex (F-strings with SQL keywords) | **Detection Only:** Identifies critical risks (patching pending). |

---

## 📂 Project Structure

```text
acrs/
├── backend/
│   ├── detector/           # ML Model training and inference
│   │   ├── train_detector.py
│   │   └── ml_detector.py
│   ├── patcher/            # Code repair logic
│   │   ├── patcher.py      # AST Transformer
│   │   └── rules.py        # Regex detection rules
│   ├── validator/          # Syntax and security validation
│   ├── pipeline/           # Orchestrates Detection -> Patching -> Validation
│   └── main.py             # API Entry point
├── frontend/               # React Dashboard (if applicable)
├── data/                   # Training datasets (vuln/ vs safe/)
├── dataset_generator.py    # Script to create synthetic training data
└── models/                 # Saved SVM model and Vectorizer (.pkl)

```

---

## 🛠️ Installation & Setup

### Prerequisites

* Python 3.8+
* Node.js (for Frontend)

### 1. Backend Setup

```bash
# Clone the repository
git clone [https://github.com/your-username/acrs.git](https://github.com/your-username/acrs.git)
cd acrs

# Install Python dependencies
pip install -r backend/requirements.txt

```

### 2. Frontend Setup (Optional)

```bash
cd frontend
npm install
npm run dev

```

---

## 💻 Usage

### 1. Generate Training Data

Before training the model, generate the synthetic dataset (Access Control samples).

```bash
python dataset_generator.py

```

*Outputs to `data/safe/` and `data/vuln/`.*

### 2. Train the ML Model

Train the LinearSVC model on the generated dataset.

```bash
python -m backend.detector.train_detector

```

*Saves artifacts to `models/svm_model.pkl` and `models/tfidf_vectorizer.pkl`.*

### 3. Run the Pipeline (CLI Test)

Test the system on a vulnerable code string.

```bash
python acrs_test.py

```

### 4. Run the API Server

Start the backend server to accept code via API.

```bash
python backend/main.py

```

---

## 🧠 How It Works (Pipeline)

1. **Input:** The system accepts a raw Python code string.
2. **Preprocessing:** Code is dedented and cleaned.
3. **Detection:**
* **Step A:** The **ML Detector** calculates a confidence score based on TF-IDF features.
* **Step B:** The **Rule Engine** scans for known regex signatures.
* *Result:* If either flags the code (and no whitelist terms are found), the code is marked "Vulnerable".


4. **Remediation:**
* The **AST Patcher** parses the code tree to apply surgical fixes (e.g., adding arguments to functions).
* If AST fails, **Regex Replacement** is attempted.


5. **Validation:**
* The **Validator** compiles the patched code to ensure no syntax errors were introduced.
* It verifies that banned functions (like raw `eval`) are no longer present.



---

## ⚠️ Limitations

* **Access Control:** Currently, the system detects missing `@login_required` decorators but only adds a warning comment, requiring manual developer intervention.
* **SQL Injection:** Detection is implemented for f-string SQL queries, but automated parameterization (patching) is not yet supported.
* **Bias:** The synthetic dataset is heavily weighted towards Flask Access Control patterns; other vulnerability types rely primarily on rule-based detection.

---

## 📜 License

This project is for educational and research purposes.

```

```
