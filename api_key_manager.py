class APIKeyManager:
    def __init__(self):
        self.keys = {}

    def set_key(self, lang_pair, api_key):
        """กำหนดคีย์เฉพาะ: เช่น JA-TH, JA-ES มีคีย์คนละอัน"""
        self.keys[lang_pair] = api_key

    def get_key(self, lang_pair):
        return self.keys.get(lang_pair, None)

# ตัวอย่าง
km = APIKeyManager()
km.set_key("JA-TH","NEXUS-JPTH-789ABC")
km.set_key("JA-ES","NEXUS-JPES-123XYZ")
