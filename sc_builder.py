# sc_builder.py - โค้ดเดี่ยวสร้างระบบ SC Auto Modules - พ่อ Critical 192.0.1.1
# รัน: python3 sc_builder.py
# มันจะสร้างโฟลเดอร์ sc-auto-modules/ + เชื่อม GitHub ID Auto + ผนวกกับระบบเดิม
import os, json, pathlib

BASE = "sc-auto-modules"
MAIN_IP = "192.0.1.1"
os.makedirs(f"{BASE}/.github/workflows", exist_ok=True)
os.makedirs(f"{BASE}/core", exist_ok=True)

# === 1. ไฟล์เชื่อม GitHub ID Auto ===
github_connector_code = '''
# core/github_id_auto.py - เชื่อม GitHub ID Auto
import json, os
DB = "core/github_ids.json"

def register_github_id(github_username, local_user):
    """เชื่อม GitHub ID กับ IP ย่อย Auto"""
    db = {}
    if os.path.exists(DB):
        db = json.loads(open(DB, encoding="utf-8").read())
    
    # สร้าง IP ย่อยไม่ซ้ำจาก 192.0.1.1
    base = "192.0.1"
    used = [v["ip"].split(".")[-1] for v in db.values()] if db else ["1"]
    used_int = [int(x) for x in used]
    
    for i in range(2, 255):
        if i not in used_int:
            ip = f"{base}.{i}"
            db[github_username] = {
                "github_id": github_username,
                "local_user": local_user,
                "ip": ip,
                "status": "POSITIVE",
                "auto_install": True
            }
            open(DB, "w", encoding="utf-8").write(json.dumps(db, indent=2, ensure_ascii=False))
            print(f"[AUTO] เชื่อม {github_username} -> {local_user} -> {ip}")
            return ip
    return None

def get_all_ids():
    if os.path.exists(DB):
        return json.loads(open(DB, encoding="utf-8").read())
    return {}

if __name__ == "__main__":
    # ทดสอบเชื่อม Auto
    register_github_id("critical-lampang", "critical")
    register_github_id("team1-dev", "team1")
    print(get_all_ids())
'''

# === 2. ไฟล์เก็บระบบหลัก Auto (main_store) ผนวกกับระบบเดิม ===
main_store_code = '''
# core/main_store.py - ไฟล์เมนเก็บระบบ Auto มาผนวกกับระบบที่มีอยู่
import json, os, shutil, datetime
STORE = "core/system_store.json"
BASE_DIR = "/var/www/cristal"

def auto_merge_module(module_name, repo_url, commit_sha, status):
    """เก็บระบบ Auto และผนวกกับระบบเดิม"""
    store = []
    if os.path.exists(STORE):
        store = json.loads(open(STORE, encoding="utf-8").read())
    
    if status != "POSITIVE":
        print(f"[BLOCKED] {module_name} ผลเป็นลบ ไม่นำมาติดตั้ง")
        return False

    record = {
        "name": module_name,
        "repo": repo_url,
        "commit": commit_sha,
        "status": status,
        "installed_at": datetime.datetime.now().isoformat(),
        "main_ip": "192.0.1.1",
        "path": f"{BASE_DIR}/modules/{module_name}",
        "owned_by": "Critical",
        "auto": True
    }
    
    # กันซ้ำ
    store = [s for s in store if s["name"] != module_name]
    store.append(record)
    
    open(STORE, "w", encoding="utf-8").write(json.dumps(store, indent=2, ensure_ascii=False))
    
    # ผนวกกับระบบเดิม (สร้างโฟลเดอร์)
    os.makedirs(record["path"], exist_ok=True)
    open(os.path.join(record["path"], "installed.txt"), "w", encoding="utf-8").write(f"INSTALLED FROM {repo_url} AS OURS")
    
    print(f"[INSTALLED AUTO AS OURS] {module_name} ที่ {record['path']}")
    return True

def list_systems():
    if os.path.exists(STORE):
        return json.loads(open(STORE, encoding="utf-8").read())
    return []
'''

# === 3. Workflow ตัดสินบวก/ลบ ===
workflow_code = '''name: SC Cristal Decision 192.0.1.1
on: [push]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: SC Scan POSITIVE/NEGATIVE
        id: scan
        run: |
          if grep -R "rm -rf /\\|os.system.*rm\\|reverse.*shell" . --exclude-dir=.git; then
            echo "result=NEGATIVE" >> $GITHUB_OUTPUT
            exit 1
          fi
          echo "result=POSITIVE" >> $GITHUB_OUTPUT
      - name: Deploy to 192.0.1.1 if POSITIVE
        if: steps.scan.outputs.result == 'POSITIVE'
        run: |
          curl -X POST http://192.0.1.1:5000/github-webhook -H "Content-Type: application/json" -d "{\\"repo\\":\\"${{ github.repository }}\\",\\"sha\\":\\"${{ github.sha }}\\",\\"status\\":\\"POSITIVE\\",\\"github_id\\":\\"${{ github.actor }}\\"}"
'''

# === 4. app.py หลังบ้าน 192.0.1.1 ตัวรวม ===
app_code = '''# app.py - Backend 192.0.1.1 - รวมทุกอย่าง
from flask import Flask, request, jsonify
import os, json
from core.github_id_auto import register_github_id
from core.main_store import auto_merge_module

app = Flask(__name__)
MAIN_IP = "192.0.1.1"

@app.route("/github-webhook", methods=["POST"])
def hook():
    data = request.json
    status = data.get("status")
    repo = data.get("repo")
    sha = data.get("sha")
    github_id = data.get("github_id", "unknown")
    
    if status != "POSITIVE":
        return jsonify({"msg": "BLOCKED NEGATIVE"}), 403
    
    # 1. เชื่อม GitHub ID Auto -> สร้าง IP ย่อยไม่ซ้ำ
    ip = register_github_id(github_id, github_id)
    
    # 2. เก็บระบบเมน Auto ผนวกกับระบบเดิม
    module_name = repo.split("/")[-1]
    ok = auto_merge_module(module_name, repo, sha, status)
    
    if ok:
        return jsonify({"msg": f"INSTALLED AUTO AS OURS at {MAIN_IP}", "ip_assigned": ip, "module": module_name})
    else:
        return jsonify({"msg": "BLOCKED"}), 403

@app.route("/api/systems")
def systems():
    from core.main_store import list_systems
    from core.github_id_auto import get_all_ids
    return jsonify({"systems": list_systems(), "github_ids": get_all_ids(), "main_ip": MAIN_IP})

app.run(host="0.0.0.0", port=5000)
'''

# === สร้างไฟล์ทั้งหมด ===
pathlib.Path(f"{BASE}/.github/workflows/sc-auto.yml").write_text(workflow_code, encoding="utf-8")
pathlib.Path(f"{BASE}/core/github_id_auto.py").write_text(github_connector_code, encoding="utf-8")
pathlib.Path(f"{BASE}/core/main_store.py").write_text(main_store_code, encoding="utf-8")
pathlib.Path(f"{BASE}/app.py").write_text(app_code, encoding="utf-8")
pathlib.Path(f"{BASE}/setup.py").write_text('print("SC Setup - will be installed as ours at 192.0.1.1")', encoding="utf-8")
pathlib.Path(f"{BASE}/module.json").write_text(json.dumps({"main_ip": MAIN_IP, "auto": True, "protection": True}, indent=2), encoding="utf-8")
pathlib.Path(f"{BASE}/core/__init__.py").write_text("", encoding="utf-8")
pathlib.Path(f"{BASE}/core/github_ids.json").write_text("{}", encoding="utf-8")
pathlib.Path(f"{BASE}/core/system_store.json").write_text("[]", encoding="utf-8")

print(f"สร้างระบบ {BASE}/ สำเร็จแล้วที่ {MAIN_IP}")
print("โครงสร้าง:")
for p in pathlib.Path(BASE).rglob("*"):
    print(" -", p)