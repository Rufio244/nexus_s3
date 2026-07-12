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
# 📌 เพิ่ม import ด้านบน
from models import core, biz, cms, sys_lock

# 📌 เพิ่มเป็นอันดับแรก ก่อนทุกหน้า
@app.before_request
def check_system_lock():
    # อนุญาตเฉพาะหน้าปลดล็อค และส่วนตรวจสอบรหัส
    if not sys_lock.check_access() and request.path not in ["/unlock-system", "/api/check-unlock"]:
        return redirect("/unlock-system")

# 📌 เพิ่มหน้าจอปลดล็อค
@app.route("/unlock-system", methods=["GET","POST"])
def unlock_page():
    if request.method == "POST":
        res = sys_lock.unlock(request.form["master_code"])
        if res["ok"]:
            return redirect("/dashboard")
        return render_template("unlock.html", msg=res["msg"])
    return render_template("unlock.html")

# 📌 เพิ่ม API ควบคุมล็อค-ปลดล็อค
@app.route("/api/lock-all", methods=["POST"])
def lock_all():
    data = request.json
    return jsonify(sys_lock.lock_all(data["code"]))

@app.route("/api/status-system")
def sys_status():
    return jsonify({"locked": sys_lock.system_locked})

