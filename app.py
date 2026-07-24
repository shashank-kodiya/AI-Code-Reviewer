from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("review.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    code = data.get("code", "")
    return jsonify(analyze_code(code))

def analyze_code(code):
    issues = []

    try:
        compile(code, "<string>", "exec")
    except SyntaxError as e:
        issues.append({
            "type": "fatal-error",
            "line": e.lineno or 0,
            "message": f"Syntax error: {e.msg}",
            "tip": "Check indentation, missing colons, or unmatched parentheses."
        })
        return {"issues": issues, "score": 0, "errors": 1, "warnings": 0}

 
    security_patterns = [
        ("os.system", "Avoid using os.system() with untrusted input."),
        ("eval(", "Use of eval() is unsafe; prefer safer alternatives."),
        ("exec(", "Use of exec() can lead to code injection."),
    ]

    for pattern, tip in security_patterns:
        if pattern in code:
            issues.append({
                "type": "security",
                "line": 0,
                "message": f"Use of insecure function detected: {pattern}",
                "tip": tip
            })

   
    if "print(" in code:
        issues.append({
            "type": "warning",
            "line": 0,
            "message": "Print statement found — avoid print() in production code.",
            "tip": "Use logging module for maintainability."
        })

    return {
        "issues": issues,
        "score": max(0, 100 - len(issues)*10),
        "errors": sum(1 for i in issues if i["type"] in ["error","fatal-error"]),
        "warnings": sum(1 for i in issues if i["type"]=="warning")
    }

if __name__ == "__main__":
    app.run(debug=True)
    import os
    port = int(os.environ.get("PORT", 5000))  
    app.run(host="0.0.0.0", port=port, debug=True)
