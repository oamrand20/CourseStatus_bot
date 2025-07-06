
import requests
import json
import time
import os

# إعدادات التليغرام
BOT_TOKEN = "8177518095:AAEzCPd5m9TeezrI-vkBtNPbR286pldFu8w"
CHAT_ID = "@tasjeeltasharuk"

# كوكي الجلسة لموقع Jadwali
SESSION_TOKEN = eyJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiT21hciBBdHRpZWgiLCJlbWFpbCI6Im9hYXRpZWgyMUBjaXQuanVzdC5lZHUuam8iLCJzdWIiOiI4NmM4YThjZS01YjY1LTQ5MWItOTExNy1kMjNiM2I2ZWFlNDEiLCJyb2xlIjoiU1RVREVOVCIsImZpcnN0TmFtZSI6Ik9tYXIiLCJsYXN0TmFtZSI6IkF0dGllaCIsImlhdCI6MTc1MTc3OTk0NCwiZXhwIjoxNzU0MzcxOTQ0fQ.Hdjx-xGQC2937OT4ETjyy6MPzhoDUvWw7CAoy8ldT0M"  

# أكواد المواد
COURSE_IDS = [
    "821192", "801022", "821104", "841000", "2510990", "2511010", "2511030",
    "2511080", "802000", "821531", "821052", "821360", "821004", "821002",
    "821090", "821001", "822111", "822133", "822121", "822141", "821051",
    "822011", "822002", "822001", "822000", "822004"
]

# ملف التخزين للحالات السابقة
STATUS_FILE = "status.json"

# headers و payload للطلب
HEADERS = {
    "Content-Type": "application/json",
    "Cookie": f"authjs.session-token={SESSION_TOKEN}"
}

PAYLOAD = {
    "onlyAvailable": False,
    "coursesLineNumbers": COURSE_IDS,
    "days": ["sun", "mon", "tue", "wed", "thu"],
    "startTime": 8.5,
    "endTime": 18,
    "pinnedSections": []
}

# تحميل الحالات السابقة من الملف
def load_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {}

# حفظ الحالات الجديدة في الملف
def save_status(data):
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f)

# إرسال تليغرام
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

# فحص المواد
def check_courses(prev_status):
    try:
        response = requests.post("https://www.jadwali.app/api/generate", headers=HEADERS, json=PAYLOAD)
        data = response.json()

        new_status = {}

        for item in data.get("schedules", []):
            for section in item.get("sections", []):
                key = f'{section["courseName"]}-{section["sectionNumber"]}'
                status = section["status"]
                new_status[key] = status

                # إذا تغيرت من مغلقة إلى مفتوحة ➜ أرسل إشعار
                if status == "مفتوحة" and prev_status.get(key) != "مفتوحة":
                    msg = (
                        f"📢 *مادة مفتوحة!*\n"
                        f"*المادة:* {section['courseName']}\n"
                        f"*الشعبة:* {section['sectionNumber']}\n"
                        f"*الحالة:* ✅ مفتوحة\n"
                        f"*الوقت:* {section['time']}"
                    )
                    send_telegram(msg)

        return new_status

    except Exception as e:
        print("❌ خطأ أثناء الاتصال:", e)
        return prev_status

# ✅ حلقة كل 10 دقائق
def main_loop():
    prev_status = load_status()
    while True:
        print("🔍 جاري التحقق من حالة المواد...")
        prev_status = check_courses(prev_status)
        save_status(prev_status)
        time.sleep(600)  # كل 10 دقائق

if __name__ == "__main__":
    main_loop()