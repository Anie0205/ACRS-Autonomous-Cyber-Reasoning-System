import os
import random

VULN_DIR = "data/vuln"
SAFE_DIR = "data/safe"
os.makedirs(VULN_DIR, exist_ok=True)
os.makedirs(SAFE_DIR, exist_ok=True)

# Templates for Broken Access Control
vuln_templates = [
    """
@app.route('/admin')
def admin_panel():
    return "Welcome Master"
""",
    """
@app.route('/dashboard/users')
def show_users():
    # VULN: Sensitive data without auth
    return db.get_all_users()
""",
    """
@app.route('/api/v1/delete_user')
def delete_user():
    id = request.args.get('id')
    db.delete(id)
    return "Deleted"
""",
    """
class AdminView(MethodView):
    def get(self):
        return render_template('admin.html')
"""
]

safe_templates = [
    """
@app.route('/admin')
@login_required
def admin_panel():
    return "Welcome Master"
""",
    """
@app.route('/dashboard/users')
@jwt_required()
def show_users():
    return db.get_all_users()
""",
    """
@app.route('/api/v1/delete_user')
@auth.login_required
def delete_user():
    if not current_user.is_admin:
        abort(403)
    id = request.args.get('id')
    db.delete(id)
    return "Deleted"
""",
    """
class AdminView(MethodView):
    decorators = [login_required]
    def get(self):
        return render_template('admin.html')
"""
]

print("Generating 100 Flask Access Control training samples...")

# Generate variations to prevent overfitting to exact strings
for i in range(50):
    # Create Vulnerable Sample
    v_code = random.choice(vuln_templates)
    # Add random noise so the model doesn't just memorize the string
    v_code = f"# Sample {i}\nfrom flask import Flask\napp = Flask(__name__)\n" + v_code
    
    with open(f"{VULN_DIR}/flask_access_vuln_{i}.py", "w") as f:
        f.write(v_code)

    # Create Safe Sample
    s_code = random.choice(safe_templates)
    s_code = f"# Sample {i}\nfrom flask import Flask\nfrom flask_login import login_required\n" + s_code
    
    with open(f"{SAFE_DIR}/flask_access_safe_{i}.py", "w") as f:
        f.write(s_code)

print("Done. Now the model has enough data to learn the difference.")