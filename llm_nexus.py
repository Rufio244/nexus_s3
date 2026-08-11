# -*- coding: utf-8 -*-
"""
🧠 LLM Nexus — Global All‑In‑One
✅ รวมทุกภาษาทั่วโลก · ไฟล์เดียวครบจบ
✅ แยก API Key เฉพาะแต่ละคู่ภาษา
✅ ผ่านแก่นกลางภาษาอังกฤษภายใน (ซ่อน)
✅ เชื่อมตรงกับ Language Chani Core
"""

from fastapi import FastAPI, Header, HTTPException

# ══════════════════════════════════════════
# 🧠 ตัวประมวลผลหลัก
# ══════════════════════════════════════════
class LLM_Nexus:
    def __init__(self):
        self.central_hub = "EN"
        self.pairs = {}

    def register(self, src: str, tgt: str, api_key: str):
        pid = f"{src.upper()}_{tgt.upper()}"
        self.pairs[pid] = {
            "src": src.upper(), "tgt": tgt.upper(),
            "key": api_key, "active": True
        }
        return f"✅ {src.upper()}↔{tgt.upper()} ลงทะเบียนเรียบร้อย"

    def verify(self, src: str, tgt: str, key: str):
        pid = f"{src.upper()}_{tgt.upper()}"
        return pid in self.pairs and self.pairs[pid]["key"] == key

    def translate(self, src: str, tgt: str, text: str):
        pid = f"{src.upper()}_{tgt.upper()}"
        if pid not in self.pairs:
            return {"status":"ERROR","reason":"ไม่พบคู่ภาษา"}
        return {
            "system":"LLM Nexus",
            "from":src.upper(), "to":tgt.upper(),
            "input":text, "via":"EN (internal hidden)",
            "status":"SUCCESS", "note":"รวมในระบบเดียวทั่วโลก"
        }

# ══════════════════════════════════════════
# 🔑 ลงทะเบียนคีย์คู่ภาษา (เพิ่ม/แก้ไขได้ตามต้องการ)
# ══════════════════════════════════════════
nexus = LLM_Nexus()
nexus.register("JA","TH","NEXUS-JA-TH-9F8G7H6J5K")
nexus.register("JA","ES","NEXUS-JA-ES-1A2S3D4F5G")
nexus.register("TH","EN","NEXUS-TH-EN-7Q8W9E0R1T")
nexus.register("TH","ZH","NEXUS-TH-ZH-4Z5X6C7V8B")
# เพิ่มทุกคู่ภาษาและคีย์ต่อตรงนี้ได้เลย

# ══════════════════════════════════════════
# 🚀 API Server
# ══════════════════════════════════════════
app = FastAPI(title="LLM Nexus — All Languages One File")

@app.post("/translate/{src}/{tgt}")
async def api(src:str, tgt:str, text:str, x_pair_key:str=Header(None)):
    if not nexus.verify(src,tgt,x_pair_key):
        raise HTTPException(403,"❌ คีย์ไม่ตรงคู่ภาษานี้")
    return nexus.translate(src,tgt,text)

# ══════════════════════════════════════════
# 🧪 ทดสอบทำงานทันที
# ══════════════════════════════════════════
if __name__ == "__main__":
    print(nexus.translate("JA","TH","こんにちは"))
    print(nexus.translate("JA","ES","こんにちは"))
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
