#!/usr/bin/env python3
"""
main.py
-------
Interactive Entry Point for ACRS.
"""

import argparse
import os
import sys

# [FIX] Add the project root directory to Python's path
# This allows 'python acrs/main.py' to work without -m
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from acrs.pipeline.acrs import ACRSPipeline

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_user_input():
    """Interactive mode to get code from file or paste."""
    print("\n--- ACRS Input Selection ---")
    print("1. Upload File (Enter Path)")
    print("2. Paste Raw Code")
    choice = input("Select option (1/2): ").strip()

    if choice == "1":
        path = input("Enter file path: ").strip()
        if not os.path.exists(path):
            print(f"Error: File '{path}' not found.")
            sys.exit(1)
        with open(path, "r", encoding="utf-8") as f:
            return f.read(), path
    
    elif choice == "2":
        print("\nPaste your Python code below. (Press Ctrl+D or Ctrl+Z on new line to finish):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        return "\n".join(lines), "pasted_code.py"
    
    else:
        print("Invalid choice.")
        sys.exit(1)

def print_final_report(result):
    """Prints the structured output requested."""
    detected = result["detected"]
    
    # Calculate scores
    vuln_confidence = result["ml_confidence"] 
    safety_score = (1.0 - vuln_confidence) if detected else vuln_confidence
    
    print("\n" + "="*60)
    print("                 ACRS FINAL REPORT")
    print("="*60)
    
    # 1. Vulnerable / Non-vulnerable
    status = "VULNERABLE" if detected else "NON-VULNERABLE"
    status_color = "\033[91m" if detected else "\033[92m" # Red/Green ANSI
    reset = "\033[0m"
    
    print(f"Status:       {status_color}{status}{reset}")
    
    # 2. Safety Score
    print(f"Safety Score: {safety_score * 100:.2f}%")
    
    if detected:
        print(f"Vuln Type:    {result['vulnerability_type']}")
        
        # 3. Patch Score
        print(f"Patch Score:  {result['patch_score']:.2f} / 1.0")
        print(f"Validated:    {'YES' if result['validated'] else 'NO'}")
        
        print("-" * 60)
        print("PATCHED CODE PREVIEW:")
        print("-" * 60)
        print(result['patched_code'].strip())
        print("-" * 60)
        
        # Save option
        save = input("\nSave patched code to file? (y/n): ").lower()
        if save == 'y':
            with open("patched_output.py", "w", encoding="utf-8") as f:
                f.write(result['patched_code'])
            print("Saved to 'patched_output.py'")
    else:
        print("\nCode appears safe. No patching required.")
    
    print("="*60 + "\n")

def main():
    parser = argparse.ArgumentParser(description="ACRS - CLI Mode")
    parser.add_argument("--file", type=str, help="Path to file")
    parser.add_argument("--code", type=str, help="Raw code string")
    args = parser.parse_args()

    # Initialize Pipeline
    # Ensure you have run 'python acrs/detector/train_detector.py' first!
    acrs = ACRSPipeline(ml_model_path="models")

    # Get Input
    if args.file:
        with open(args.file, "r") as f:
            code = f.read()
    elif args.code:
        code = args.code
    else:
        # Interactive mode if no args passed
        code, _ = get_user_input()

    # Run Pipeline
    result = acrs.process(code)

    # Output Results
    print_final_report(result)

if __name__ == "__main__":
    main()