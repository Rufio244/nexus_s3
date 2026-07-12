from pymongo import MongoClient
import hashlib, uuid, time
from config import *

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]
COL = {
    "root": db.semantic_root, "links": db.meaning_links,
    "users": db.users, "orders": db.orders, "content": db.web_content
}

class ChaniCore:
    root_ready = False
    def build_root(self, data):
        for w,m in data.items(): COL["root"].update_one({"w":w},{"$set":{"w":w,"m":m}},upsert=True)
        self.root_ready = True
        return {"ok":True,"count":len(data)}

    def connect_lang(self, code, pairs):
        if not self.root_ready: return {"err":"ต้องสร้างแก่นไทยก่อน"}
        for f,t in pairs.items(): COL["links"].update_one({"l":code,"f":f},{"$set":{"l":code,"f":f,"t":t}},upsert=True)
        return {"ok":True}

    def translate_deep(self, text, lang):
        res = []
        for w in text.split():
            lnk = COL["links"].find_one({"l":lang,"f":w.lower()})
            root = COL["root"].find_one({"w":lnk["t"]}) if lnk else None
            res.append(f"{w} → {root['m'] if root else 'ไม่พบ'}")
        return {"res":" | ".join(res)}

class Business:
    plans = {"FREE":0,"BASIC":149,"PRO":499,"MASTER":1999,"PRANAI":4999}
    def reg(self, em, nm, pw):
        if COL["users"].find_one({"e":em}): return {"exists":1}
        uid = f"NX-{str(uuid.uuid4())[:6]}"
        COL["users"].insert_one({"id":uid,"e":em,"n":nm,"p":hashlib.sha256(pw.encode()).hexdigest(),"plan":"FREE"})
        return {"uid":uid}
    def pay(self, uid, plan):
        oid = f"ORD-{uuid.uuid4().hex[:8]}"
        COL["orders"].insert_one({"id":oid,"u":uid,"pl":plan,"pr":self.plans[plan],"st":"WAIT"})
        return {"oid":oid}
    def confirm(self, oid):
        o = COL["orders"].find_one({"id":oid})
        COL["orders"].update_one({"id":oid},{"$set":{"st":"OK"}})
        COL["users"].update_one({"id":o["u"]},{"$set":{"plan":o["pl"]}})
        return {"ok":True}

class CMS:
    def save(self, pg, fd, val):
        COL["content"].update_one({"p":pg,"f":fd},{"$set":{"v":val}},upsert=True)
    def get(self, pg):
        return {x["f"]:x["v"] for x in COL["content"].find({"p":pg})}

core = ChaniCore()
biz = Business()
cms = CMS()

