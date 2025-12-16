#!/usr/bin/env python3
"""
api_wrapper.py
--------------
Flask API wrapper for ACRS backend to connect with frontend.
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# Setup paths - same as main.py and gui.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from backend.pipeline.acrs import ACRSPipeline

# --- Configuration ---
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend development

# Model paths - models are in the acrs directory
MODELS_DIR = os.path.join(current_dir, "models")
if not os.path.exists(MODELS_DIR):
    MODELS_DIR = os.path.join(parent_dir, "models")  # Fallback to parent directory
    if not os.path.exists(MODELS_DIR):
        MODELS_DIR = "models"  # Final fallback to relative path

# Initialize ACRS Pipeline
try:
    acrs_pipeline = ACRSPipeline(ml_model_path=MODELS_DIR)
    print(f"[INFO] ACRS Pipeline initialized successfully with models from: {MODELS_DIR}")
except Exception as e:
    print(f"[ERROR] Failed to initialize ACRS Pipeline: {e}")
    print(f"[ERROR] Make sure models are available at: {MODELS_DIR}")
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
    
    Returns:
    {
        "status": "success",
        "report": {
            "success": bool,
            "detected": bool,
            "ml_confidence": float,
            "vulnerability_type": str,
            "patch_score": float,
            "patched_code": str,
            "validated": bool
        }
    }
    """
    if acrs_pipeline is None:
        return jsonify({
            "error": "ACRS Pipeline failed to initialize. Check model files.",
            "hint": f"Expected models at: {MODELS_DIR}"
        }), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400
    
    code_input = data.get('code')
    if not code_input:
        return jsonify({"error": "Missing 'code' in request body"}), 400

    try:
        # Run the ACRS pipeline
        result = acrs_pipeline.process(code_input)
        
        # Return the result directly (matches backend format)
        return jsonify({
            "status": "success",
            "report": result
        }), 200

    except Exception as e:
        # Log the error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"[ERROR] Error during ACRS analysis: {e}")
        print(f"[ERROR] Traceback: {error_trace}")
        return jsonify({
            "error": f"An internal error occurred during analysis: {str(e)}"
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Simple status check endpoint.
    """
    status = "ready" if acrs_pipeline is not None else "initialization_failed"
    return jsonify({
        "service": "ACRS API Wrapper",
        "status": status,
        "model_loaded": acrs_pipeline is not None,
        "models_path": MODELS_DIR
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("ACRS Flask API Wrapper")
    print("=" * 60)
    print(f"Models directory: {MODELS_DIR}")
    print(f"Pipeline status: {'Ready' if acrs_pipeline is not None else 'Failed'}")
    print("=" * 60)
    print("Starting Flask server on http://0.0.0.0:5000")
    print("API endpoints:")
    print("  GET  /api/status  - Check service status")
    print("  POST /api/analyze - Analyze Python code")
    print("=" * 60)
    
    # Run the Flask app on the environment's PORT or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False) # Turn off debug for production

