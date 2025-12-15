import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from acrs.pipeline.acrs import ACRSPipeline

# --- Configuration ---
app = Flask(__name__)
CORS(app) # Enable CORS for frontend development
ACRS_MODEL_PATH = "models/svm_model.pkl"
ACRS_VECTORIZER_PATH = "models/tfidf_vectorizer.pkl"
MAX_ITERATIONS = 5

# Initialize ACRS Pipeline (assuming models are present)
try:
    acrs_pipeline = ACRSPipeline(
        ml_model_path=ACRS_MODEL_PATH,
        vectorizer_path=ACRS_VECTORIZER_PATH,
        max_iterations=MAX_ITERATIONS,
        save_patches=False # No need to save to disk in API
    )
except Exception as e:
    print(f"Error initializing ACRS Pipeline: {e}")
    acrs_pipeline = None

# --- API Endpoints ---

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """
    Endpoint to run the ACRS pipeline on a given code snippet.
    
    Expected JSON body:
    {
        "code": "print(eval(input()))"
    }
    """
    if acrs_pipeline is None:
        return jsonify({"error": "ACRS Pipeline failed to initialize. Check model files."}), 500

    data = request.get_json()
    code_input = data.get('code')

    if not code_input:
        return jsonify({"error": "Missing 'code' in request body"}), 400

    try:
        # The acrs.run() method takes the code directly
        result = acrs_pipeline.run(code_input)
        
        # The result object already contains the full report and patched code
        return jsonify({
            "status": "success",
            "report": result
        }), 200

    except Exception as e:
        # Log the error for debugging
        print(f"Error during ACRS run: {e}")
        return jsonify({"error": f"An internal error occurred during analysis: {str(e)}"}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Simple status check endpoint.
    """
    status = "ready" if acrs_pipeline is not None else "initialization_failed"
    return jsonify({
        "service": "ACRS API Wrapper",
        "status": status,
        "model_loaded": acrs_pipeline is not None
    }), 200

if __name__ == '__main__':
    # Run the Flask app on port 5000
    app.run(host='0.0.0.0', port=5000)
