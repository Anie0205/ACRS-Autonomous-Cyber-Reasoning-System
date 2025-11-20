#!/usr/bin/env python3
"""
main.py
-------

Entry point for running the Autonomous Cyber Reasoning System (ACRS).

This script provides a clean CLI for:

    - Loading code samples (file or raw string)
    - Running the full ACRS pipeline:
            ML Detection →
            Rule-based Analysis →
            Patch Generation →
            Patch Ranking →
            Patch Validation →
            Multi-iteration Refinement
    - Returning a structured final report
    - Writing patched code to disk

Everything in this file is intentionally simple, transparent,
and CPU-friendly. No GPU, no cloud, no LLM.
"""

import argparse
import json
import os

from acrs.pipeline.acrs import ACRSPipeline


# ---------------------------------------------------------
# CLI Utilities
# ---------------------------------------------------------

def parse_cli():
    """
    Parses command-line arguments.

    You can run either:
        python main.py --file script.py
    or
        python main.py --code "print(eval(input()))"
    """
    parser = argparse.ArgumentParser(
        description="Autonomous Cyber Reasoning System (ACRS)"
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Path to Python source file to analyze"
    )

    parser.add_argument(
        "--code",
        type=str,
        help="Raw Python code as input (alternative to --file)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="models/svm_model.pkl",
        help="Path to trained SVM ML model"
    )

    parser.add_argument(
        "--vectorizer",
        type=str,
        default="models/tfidf_vectorizer.pkl",
        help="Path to TF-IDF vectorizer"
    )

    parser.add_argument(
        "--max-iter",
        type=int,
        default=5,
        help="Maximum patch-refinement iterations"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="patched_output.py",
        help="Where to save the final patched code"
    )

    return parser.parse_args()


# ---------------------------------------------------------
# Pretty Print Helpers
# ---------------------------------------------------------

def print_banner():
    print("=" * 70)
    print("       AUTONOMOUS CYBER REASONING SYSTEM (ACRS) — CPU EDITION")
    print("=" * 70)
    print("This system uses:")
    print(" • ML-based vulnerability detection (SVM + TF-IDF)")
    print(" • Rule-based static analysis")
    print(" • AST-driven patch generation")
    print(" • ML patch ranking")
    print(" • Sandboxed execution validation")
    print("=" * 70)
    print()


def print_final_report(result: dict):
    """
    Prints a human-readable final summary of the ACRS run.
    """

    print("\n====================== FINAL ACRS REPORT ======================")
    print(f"Success: {result['success']}")
    print(f"Iterations used: {result['iterations']}")
    print("\n--- Vulnerability Reports Each Iteration ---")

    for i, rep in enumerate(result["reports"], 1):
        print(f"\n[Iteration {i}]")
        print(f" ML Label: {rep['ml_label']} (1 = vulnerable)")
        print(f" ML Score: {rep['ml_score']:.4f}")
        print(f" Rule-Based Findings: {rep['rule_findings']}")

    print("\n===============================================================")


# ---------------------------------------------------------
# Main Runner
# ---------------------------------------------------------

def main():
    print_banner()
    args = parse_cli()

    # Check input sources
    if not args.file and not args.code:
        print("Error: provide either --file or --code")
        return

    # Initialize ACRS with paths to ML model + vectorizer
    acrs = ACRSPipeline(
        ml_model_path=args.model,
        vectorizer_path=args.vectorizer,
        max_iterations=args.max_iter,
        save_patches=True
    )

    # Load input
    code_source = args.file if args.file else args.code

    # Run the full autonomous loop
    result = acrs.run(code_source)

    # Save patched code or original (if clean)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(result["patched_code"])

    print(f"\nPatched code written to: {args.output}")

    # Print readable report
    print_final_report(result)

    # Also dump JSON for automation
    json_report_path = "acrs_report.json"
    with open(json_report_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

    print(f"JSON report saved as: {json_report_path}")


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()
