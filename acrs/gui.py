import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
import sys
import threading

# --- 1. SETUP PATHS (Fixes ModuleNotFoundError) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from acrs.pipeline.acrs import ACRSPipeline

# --- 2. INITIALIZE PIPELINE ---
# We load this once at startup
try:
    pipeline = ACRSPipeline(ml_model_path=os.path.join(parent_dir, "models"))
except Exception as e:
    messagebox.showerror("Init Error", f"Failed to load models:\n{e}\n\nDid you run 'train_detector.py'?")
    sys.exit(1)

# --- 3. GUI LOGIC ---
def run_scan():
    """Runs the analysis when button is clicked."""
    code = txt_input.get("1.0", tk.END).strip()
    
    if not code:
        messagebox.showwarning("Empty Input", "Please paste some Python code to analyze.")
        return

    # Disable button while processing
    btn_scan.config(state=tk.DISABLED, text="Analyzing...")
    txt_output.delete("1.0", tk.END)
    
    def process_thread():
        try:
            # Run the ACRS pipeline
            result = pipeline.process(code)
            
            # Format the report
            report = format_report(result)
            
            # Update GUI (must be on main thread)
            root.after(0, lambda: display_result(report))
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", f"An error occurred during analysis:\n{e}"))
        finally:
            root.after(0, lambda: btn_scan.config(state=tk.NORMAL, text="Analyze & Patch"))

    # Run in background thread to keep GUI responsive
    threading.Thread(target=process_thread, daemon=True).start()

def format_report(result):
    """Generates the text report for the output box."""
    detected = result["detected"]
    vuln_conf = result["ml_confidence"]
    safety_score = (1.0 - vuln_conf) if detected else vuln_conf
    
    lines = []
    lines.append("=" * 50)
    lines.append("              ACRS ANALYSIS REPORT")
    lines.append("=" * 50)
    
    status = "VULNERABLE" if detected else "SAFE"
    lines.append(f"STATUS:       {status}")
    lines.append(f"SAFETY SCORE: {safety_score * 100:.2f}%")
    
    if detected:
        lines.append(f"THREAT TYPE:  {result['vulnerability_type']}")
        lines.append(f"PATCH SCORE:  {result.get('patch_score', 0):.2f} / 1.0")
        lines.append(f"VALIDATED:    {'YES' if result['validated'] else 'NO'}")
        lines.append("-" * 50)
        lines.append("PATCHED CODE:")
        lines.append("-" * 50)
        lines.append(result['patched_code'])
    else:
        lines.append("\nNo vulnerabilities detected.")
        
    return "\n".join(lines)

def display_result(report_text):
    """Inserts text into output box."""
    txt_output.insert(tk.END, report_text)

# --- 4. BUILD WINDOW ---
root = tk.Tk()
root.title("ACRS - Autonomous Cyber Reasoning System")
root.geometry("900x700")

# Input Section
lbl_input = tk.Label(root, text="Paste Source Code Here:", font=("Arial", 10, "bold"))
lbl_input.pack(anchor="w", padx=10, pady=(10, 0))

txt_input = scrolledtext.ScrolledText(root, height=15, font=("Consolas", 10))
txt_input.pack(fill="both", expand=True, padx=10, pady=5)

# Button
btn_scan = tk.Button(root, text="Analyze & Patch", font=("Arial", 12, "bold"), 
                     bg="#4CAF50", fg="white", command=run_scan)
btn_scan.pack(pady=10, ipadx=20, ipady=5)

# Output Section
lbl_output = tk.Label(root, text="Analysis Results & Patched Code:", font=("Arial", 10, "bold"))
lbl_output.pack(anchor="w", padx=10, pady=(5, 0))

txt_output = scrolledtext.ScrolledText(root, height=15, font=("Consolas", 10), bg="#f4f4f4")
txt_output.pack(fill="both", expand=True, padx=10, pady=10)

# Start
if __name__ == "__main__":
    root.mainloop()