from flask import Flask, render_template, request, redirect, session, jsonify
from certificate import issue_cert, verify_cert
from qr_utils import generate_qr
from config import ADMIN_WALLET
from web3 import Web3
from eth_account.messages import encode_defunct
from config import RPC_URL


app = Flask(__name__)
app.secret_key = "certichain_secret"

# ================= LOGIN =================

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/auth", methods=["POST"])
def auth():
    try:
        data = request.json

        address = data.get("address")
        signature = data.get("signature")
        message = data.get("message")

        msg = encode_defunct(text=message)

        recovered = Web3().eth.account.recover_message(
            msg,
            signature=signature
        )

        if recovered.lower() == address.lower():
            session["user"] = address
            print("✅ LOGIN SUCCESS:", address)
            return jsonify({"success": True})

        print("❌ SIGNATURE MISMATCH")
        return jsonify({"success": False})

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False})


# ================= DASHBOARD =================

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    is_admin = session["user"].lower() == ADMIN_WALLET.lower()

    return render_template(
        "dashboard.html",
        user=session["user"],
        is_admin=is_admin
    )


# ================= ISSUE =================

@app.route("/issue", methods=["GET", "POST"])
def issue():
    if "user" not in session:
        return redirect("/")

    if session["user"].lower() != ADMIN_WALLET.lower():
        return "❌ Only admin can issue certificates"

    if request.method == "POST":
        name = request.form.get("name")
        course = request.form.get("course")

        if not name or not course:
            return "Missing data"

        cert_hash, tx = issue_cert(name, course)
        qr = generate_qr(cert_hash, cert_hash)

        return render_template(
            "result.html",
            hash=cert_hash,
            tx=tx,
            qr=qr
        )

    return render_template("issue.html")

# ================= EXPLORER =================

web3 = Web3(Web3.HTTPProvider(RPC_URL))

@app.route("/explorer")
def explorer():
    latest_block = web3.eth.block_number

    txs = []

    block = web3.eth.get_block(latest_block, full_transactions=True)

    for tx in block.transactions:
        txs.append({
            "hash": tx.hash.hex(),
            "from": tx["from"],
            "to": tx["to"]
        })

    return render_template("explorer.html", txs=txs)

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