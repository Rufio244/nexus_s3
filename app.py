from flask import Flask, render_template, request, redirect, session, jsonify
from config import SECRET_KEY, ADMIN_PLAN
from models import core, biz, cms

app = Flask(__name__)
app.secret_key = SECRET_KEY

# 📄 หน้าเว็บ
@app.route("/")
def home(): return render_template("index.html", data=cms.get("index"))
@app.route("/pricing")
def pricing(): return render_template("pricing.html", plans=biz.plans)
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u = biz.COL["users"].find_one({"e":request.form["e"]})
        if u and u["p"] == __import__("hashlib").sha256(request.form["p"].encode()).hexdigest():
            session["uid"] = u["id"]; session["plan"] = u["plan"]
            return redirect("/dashboard")
    return render_template("login.html")
@app.route("/register", methods=["GET","POST"])
def reg():
    if request.method=="POST": biz.reg(request.form["e"],request.form["n"],request.form["p"])
    return render_template("register.html")

# 🛡️ หลังบ้าน + AI + แก้ไข
@app.route("/dashboard")
def dash():
    if session.get("plan") != ADMIN_PLAN: return redirect("/login")
    return render_template("dashboard.html", users=list(biz.COL["users"].find()))

@app.route("/api/cmd", methods=["POST"])
def cmd():
    t = request.json["text"]
    if "เปลี่ยน" in t: cms.save("index", "title", t.split("เป็น")[-1].strip())
    return jsonify({"res":"✅ ทำเรียบร้อยแล้วครับ"})

@app.route("/api/save", methods=["POST"])
def save():
    d = request.json; cms.save(d["p"],d["f"],d["v"])
    return jsonify({"ok":1})

@app.route("/logout")
def out(): session.clear(); return redirect("/")

if __name__ == "__main__": app.run(port=8080, debug=True)
@app.route("/dashboard")
def dash():
    if session.get("plan") != "PRANAI":
        return redirect("/login")
    return render_template("dashboard.html", data=cms.get("index"))

