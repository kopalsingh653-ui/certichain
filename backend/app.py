from flask import Flask, render_template, request, redirect, session, jsonify
from certificate import issue_cert, verify_cert
from qr_utils import generate_qr
from config import ADMIN_WALLET
from web3 import Web3
from eth_account.messages import encode_defunct

app = Flask(__name__)
app.secret_key = "certichain_secret"

# ================= AUTH =================

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/auth", methods=["POST"])
def auth():
    data = request.json

    address = data["address"]
    signature = data["signature"]
    message = data["message"]

    msg = encode_defunct(text=message)
    recovered = Web3().eth.account.recover_message(msg, signature=signature)

    if recovered.lower() == address.lower():
        session["user"] = address
        return jsonify({"success": True})

    return jsonify({"success": False})

# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html", user=session["user"])

# ================= ISSUE =================

@app.route("/issue", methods=["GET", "POST"])
def issue():
    if "user" not in session:
        return redirect("/")

    if session["user"].lower() != ADMIN_WALLET.lower():
        return "Only admin allowed"

    if request.method == "POST":
        name = request.form["name"]
        course = request.form["course"]

        cert_hash, tx = issue_cert(name, course)
        qr = generate_qr(cert_hash, cert_hash)

        return render_template("result.html",
                               hash=cert_hash,
                               tx=tx,
                               qr=qr)

    return render_template("issue.html")

# ================= VERIFY =================

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        cert_hash = request.form["hash"]
        data = verify_cert(cert_hash)

        return render_template("result.html", data=data)

    return render_template("verify.html")

# ================= LOGOUT =================

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=True)