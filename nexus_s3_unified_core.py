#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nexus S3 Unified Core | DLB-S3
ระบบแก่นกลางภาษาไทย → เชื่อมทุกภาษาโลก
เรียนรู้แบบลูกโซ่ทุกแหล่งข้อมูล | เชื่อมต่อ AI/ระบบภายนอกได้
มาตรฐาน: 1 ภาษา = 200 หน่วยความหมาย
"""

import time
import re
import json
import base64
import threading
import requests
from flask import Flask, request, jsonify

# ═══════════════════════════════════════════════
# ⚙️ การตั้งค่าระบบหลัก
# ═══════════════════════════════════════════════
APP = Flask(__name__)
SYSTEM_CONFIG = {
    "CORE_LANG": "THA",
    "CORE_NAME": "ภาษาไทย",
    "STANDARD_UNIT": 200,  # 1 ภาษา = 200 หน่วยความหมาย
    "AUTO_LEARN": True,
    "CHAIN_LEARNING": True, # เรียนรู้แบบลูกโซ่
    "API_GLOBAL_ACCESS": True
}

# 🔐 ฐานความรู้กลาง
KNOWLEDGE_BASE = {
    "LEXICON": {},          # ความหมายกลาง
    "BRIDGE": {},           # การเชื่อมโยงข้ามภาษา
    "LANG_REGISTRY": {},    # ทะเบียนภาษาโลก
    "LEARNING_LOG": []
}

# ═══════════════════════════════════════════════
# 🧠 หัวใจหลัก: ประมวลผลและเรียนรู้
# ═══════════════════════════════════════════════
class NexusCore:
    def __init__(self):
        self.running = True
        print("🚀 Nexus S3 เริ่มทำงาน — แก่นกลางภาษาไทย")
        print(f"📏 มาตรฐาน: 1 ภาษา = {SYSTEM_CONFIG['STANDARD_UNIT']} หน่วย")

    def _get_core_id(self, word_th):
        """สร้างรหัสความหมายกลางแบบมาตรฐาน"""
        return f"NX-TH-{abs(hash(word_th)) % 1000000:06d}"

    def register_language(self, code, name, region=""):
        """ลงทะเบียนภาษาใหม่ ทุกภาษาเท่ากันที่ 200 หน่วย"""
        if code not in KNOWLEDGE_BASE["LANG_REGISTRY"]:
            KNOWLEDGE_BASE["LANG_REGISTRY"][code] = {
                "name": name,
                "region": region,
                "unit_size": SYSTEM_CONFIG["STANDARD_UNIT"],
                "connected": False,
                "added_at": time.time()
            }
            print(f"🌍 ลงทะเบียนภาษา: {name} [{code}]")

    def learn_chain_source(self, source_name, data):
        """🔗 เรียนรู้แบบลูกโซ่: ดึงข้อมูล → แตกแขนง → เชื่อมโยงทั้งหมด"""
        learned = 0
        try:
            # 1. เจอรายชื่อภาษา → ลงทะเบียนทั้งลูกโซ่
            if "languages" in data:
                for lang in data["languages"]:
                    self.register_language(
                        lang.get("code"), lang.get("name"), lang.get("region","")
                    )
                learned += len(data["languages"])

            # 2. เจอคู่แปล → เชื่อมโยงทั้งไป-กลับ และกระจายลูกโซ่
            if "pairs" in data:
                for p in data["pairs"]:
                    la, ta = p.get("lang_a"), p.get("text_a","").strip().lower()
                    lb, tb = p.get("lang_b"), p.get("text_b","").strip().lower()
                    if not all([la, ta, lb, tb]): continue

                    # บันทึกสองทาง
                    KNOWLEDGE_BASE["BRIDGE"][(la, ta, lb)] = tb
                    KNOWLEDGE_BASE["BRIDGE"][(lb, tb, la)] = ta
                    learned += 2

                    # ผูกเข้ากับแก่นกลางไทย
                    if la == "THA":
                        cid = self._get_core_id(ta)
                        KNOWLEDGE_BASE["LEXICON"][cid] = {"word_th": ta, "nexus": f"⟦{ta}⟧"}
                        KNOWLEDGE_BASE["LANG_REGISTRY"][lb]["connected"] = True
                    if lb == "THA":
                        cid = self._get_core_id(tb)
                        KNOWLEDGE_BASE["LEXICON"][cid] = {"word_th": tb, "nexus": f"⟦{tb}⟧"}
                        KNOWLEDGE_BASE["LANG_REGISTRY"][la]["connected"] = True

            # 3. ลูกโซ่อัตโนมัติ: ถ้า A-ไทย, ไทย-B → เชื่อม A-B ทันที
            if SYSTEM_CONFIG["CHAIN_LEARNING"]:
                self._auto_chain_link()

            KNOWLEDGE_BASE["LEARNING_LOG"].append({
                "time": time.time(), "source": source_name, "learned": learned
            })
            print(f"🔗 เรียนรู้ลูกโซ่ {source_name}: เพิ่ม {learned} รายการ")
            return learned

        except Exception as e:
            print(f"⚠️ ผิดพลาดลูกโซ่: {e}")
            return 0

    def _auto_chain_link(self):
        """สร้างการเชื่อมโยงอัตโนมัติทั้งเครือข่าย"""
        new_links = 0
        for (l1, w1, l2), w2 in list(KNOWLEDGE_BASE["BRIDGE"].items()):
            if l2 == "THA":
                for l3 in KNOWLEDGE_BASE["LANG_REGISTRY"]:
                    if l3 in [l1, "THA"]: continue
                    if ("THA", w2, l3) in KNOWLEDGE_BASE["BRIDGE"]:
                        w3 = KNOWLEDGE_BASE["BRIDGE"][("THA", w2, l3)]
                        if (l1, w1, l3) not in KNOWLEDGE_BASE["BRIDGE"]:
                            KNOWLEDGE_BASE["BRIDGE"][(l1, w1, l3)] = w3
                            KNOWLEDGE_BASE["BRIDGE"][(l3, w3, l1)] = w1
                            new_links += 2
        if new_links > 0:
            print(f"🔗 ลูกโซ่กระจายอัตโนมัติ: เพิ่มเชื่อมโยง {new_links} เส้น")

    def translate(self, text, from_lang, to_langs):
        """แปลผ่านแก่นกลาง ไปหลายภาษาได้ครั้งเดียว"""
        # แปลงเข้าแก่นกลาง
        core_ref = []
        for w in text.split():
            clean = re.sub(r"[^a-zก-๙]", "", w.lower())
            if from_lang == "THA":
                core_ref.append(f"⟦{clean}⟧")
            elif (from_lang, clean) in KNOWLEDGE_BASE["BRIDGE"]:
                core_ref.append(f"⟦{KNOWLEDGE_BASE['BRIDGE'][(from_lang, clean)]}⟧")
            else:
                core_ref.append(f"[{clean}]")

        # แปลงออกทุกภาษาเป้าหมาย
        results = {}
        for lang in to_langs:
            out = []
            for tag in core_ref:
                wth = tag.strip("⟦⟧")
                if lang == "THA":
                    out.append(wth)
                elif ("THA", wth, lang) in KNOWLEDGE_BASE["BRIDGE"]:
                    out.append(KNOWLEDGE_BASE["BRIDGE"][("THA", wth, lang)])
                else:
                    out.append(tag)
            results[lang] = " ".join(out)

        return {
            "original": text,
            "core_middle": " ".join(core_ref),
            "translations": results
        }

    def status(self):
        return {
            "languages_total": len(KNOWLEDGE_BASE["LANG_REGISTRY"]),
            "connected_to_th": sum(1 for v in KNOWLEDGE_BASE["LANG_REGISTRY"].values() if v["connected"]),
            "meaning_units": len(KNOWLEDGE_BASE["LEXICON"]),
            "total_links": len(KNOWLEDGE_BASE["BRIDGE"]) // 2,
            "standard": f"1 lang = {SYSTEM_CONFIG['STANDARD_UNIT']} units"
        }

# ═══════════════════════════════════════════════
# 🔌 API สำหรับเชื่อมต่อ AI / ระบบภายนอก
# ═══════════════════════════════════════════════
CORE = NexusCore()

@APP.route("/api/learn", methods=["POST"])
def api_learn():
    """รับข้อมูลเพื่อเรียนรู้ — จากแหล่งใดๆ หรือ AI ภายนอก"""
    data = request.get_json()
    cnt = CORE.learn_chain_source(data.get("source","EXTERNAL"), data)
    return jsonify({"status":"ok", "learned": cnt})

@APP.route("/api/translate", methods=["POST"])
def api_trans():
    """บริการแปลภาษา — เชื่อมต่อ AI/แอปอื่นได้เลย"""
    d = request.get_json()
    return jsonify(CORE.translate(d["text"], d["from"], d["to"]))

@APP.route("/api/status", methods=["GET"])
def api_stat():
    """ตรวจสอบสถานะระบบ"""
    return jsonify(CORE.status())

@APP.route("/api/feed-global", methods=["GET"])
def auto_feed():
    """🔄 ป้อนข้อมูลลูกโซ่อัตโนมัติจากแหล่งสาธารณะ"""
    sources =
    try:
        resp = requests.get(s["url"], timeout=10)
        data = resp.json()
        total += CORE.learn_chain_source(s["name"], data)
    except:
        pass
    return jsonify({"status":"completed", "total_learned": total})

# ═══════════════════════════════════════════════
# 🤖 ตัวเชื่อมต่ออัตโนมัติ: ดึงเรียนรู้ต่อเนื่อง
# ═══════════════════════════════════════════════
def background_learner():
    """ทำงานเบื้องหลัง ดึงความรู้แบบลูกโซ่ตลอดเวลา"""
    while CORE.running:
        time.sleep(3600)  # ตรวจสอบทุก 1 ชั่วโมง
        if not SYSTEM_CONFIG["AUTO_LEARN"]:
            continue
        try:
            requests.get("http://localhost:5000/api/feed-global")
        except:
            pass

# ═══════════════════════════════════════════════
# 🚀 เริ่มทำงานทั้งระบบ
# ═══════════════════════════════════════════════
if __name__ == "__main__":
    # เริ่มเธรดเรียนรู้เบื้องหลัง
    threading.Thread(target=background_learner, daemon=True).start()
    
    # ลงทะเบียนภาษาไทยเป็นแก่นกลาง
    CORE.register_language("THA", "ภาษาไทย", "ประเทศไทย")
    
    print("="*50)
    print("  🧠 NEXUS S3 UNIFIED CORE - ระบบสมองกลางภาษา")
    print("  ✅ พร้อมเรียนรู้แบบลูกโซ่ทุกแหล่ง")
    print("  ✅ เชื่อมต่อ AI / ระบบภายนอกผ่าน API")
    print("  ✅ มาตรฐาน: 1 ภาษา = 200 หน่วยความหมาย")
    print("="*50)
    print("\n📡 API พร้อมใช้งาน:")
    print("   /api/learn    → ป้อนข้อมูลให้เรียนรู้")
    print("   /api/translate → แปลภาษา")
    print("   /api/status    → ดูสถานะความคืบหน้า")
    print("   /api/feed-global → ดึงข้อมูลโลกอัตโนมัติ")
    print("="*50)
    
    APP.run(host="0.0.0.0", port=5000, debug=False)
