import os
import random
import textwrap

# OUTPUT DIRECTORIES
VULN_DIR = "data/vuln"
SAFE_DIR = "data/safe"

os.makedirs(VULN_DIR, exist_ok=True)
os.makedirs(SAFE_DIR, exist_ok=True)

# How many samples to generate
NUM_VULN = 150
NUM_SAFE = 150


# --------------------------
# 1. Vulnerability Templates
# --------------------------

VULN_TEMPLATES = [
    # ---------- eval injection ----------
    lambda: f"user = input()\neval(user)",

    lambda: f"cmd = input('>>> ')\nresult = eval(cmd)\nprint(result)",

    # ---------- exec injection ----------
    lambda: f"data = input('code: ')\nexec(data)",

    lambda: f"code = input()\nexec(code)",

    # ---------- SQL injection ----------
    lambda: textwrap.dedent("""
        import sqlite3
        db = sqlite3.connect(':memory:')
        cur = db.cursor()
        user = input()
        query = "SELECT * FROM users WHERE id = " + user
        cur.execute(query)
    """),

    lambda: textwrap.dedent("""
        user = input("name: ")
        query = "SELECT * FROM products WHERE name = '" + user + "'"
        cursor.execute(query)
    """),

    # ---------- path traversal ----------
    lambda: textwrap.dedent("""
        filename = input("file: ")
        data = open("/data/" + filename, "r").read()
    """),

    lambda: textwrap.dedent("""
        f = input()
        with open("uploads/" + f, "rb") as fp:
            print(fp.read())
    """),

    # ---------- unsafe deserialization ----------
    lambda: textwrap.dedent("""
        import pickle
        data = input("payload: ")
        obj = pickle.loads(bytes(data, 'utf-8'))
    """),

    lambda: textwrap.dedent("""
        import jsonpickle
        payload = input()
        obj = jsonpickle.decode(payload)
    """),

    # ---------- command injection ----------
    lambda: textwrap.dedent("""
        import os
        cmd = input("cmd: ")
        os.system(cmd)
    """),

    lambda: textwrap.dedent("""
        import subprocess
        x = input("cmd: ")
        subprocess.Popen(x, shell=True)
    """),
]


# ----------------------------------------
# 2. SAFE code templates (non-vulnerable)
# ----------------------------------------

SAFE_TEMPLATES = [
    lambda: "print('Hello World')",

    lambda: textwrap.dedent("""
        x = 5
        y = 7
        print(x + y)
    """),

    lambda: textwrap.dedent("""
        def add(a, b):
            return a + b
        
        print(add(2, 3))
    """),

    lambda: textwrap.dedent("""
        name = input()
        print(name.upper())
    """),

    lambda: textwrap.dedent("""
        import sqlite3
        cur = sqlite3.connect(':memory:').cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (1,))
    """),

    lambda: textwrap.dedent("""
        import os
        filename = "data.txt"
        with open(filename, "r") as f:
            print(f.read())
    """),

    lambda: textwrap.dedent("""
        import pickle
        safe = {"a": 1}
        data = pickle.dumps(safe)
        obj = pickle.loads(data)
    """),

    lambda: textwrap.dedent("""
        import subprocess
        subprocess.run(["echo", "hello"], shell=False)
    """),

    lambda: textwrap.dedent("""
        def fib(n):
            if n <= 1:
                return n
            return fib(n-1) + fib(n-2)
    """),

    lambda: textwrap.dedent("""
        items = ["apple", "banana", "mango"]
        for i in items:
            print(i)
    """),
]


# ------------------------------
# 3. Utility: Write to File
# ------------------------------

def write_file(folder, index, content):
    fname = os.path.join(folder, f"{index:03d}.py")
    with open(fname, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[OK] Wrote {fname}")


# ------------------------------
# 4. Generate Vulnerable Samples
# ------------------------------

print("Generating vulnerable dataset...")
for i in range(1, NUM_VULN + 1):
    sample = random.choice(VULN_TEMPLATES)()
    write_file(VULN_DIR, i, sample)


# ------------------------------
# 5. Generate Safe Samples
# ------------------------------

print("\nGenerating safe dataset...")
for i in range(1, NUM_SAFE + 1):
    sample = random.choice(SAFE_TEMPLATES)()
    write_file(SAFE_DIR, i, sample)


print("\nDataset generation complete!")
