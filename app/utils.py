# server/app/utils.py
import os, uuid, shutil, zipfile, json
from fastapi import UploadFile

BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def save_upload_file(upload_file: UploadFile, prefix: str = "") -> str:
    ext = os.path.splitext(upload_file.filename)[1] or ".bin"
    name = prefix + uuid.uuid4().hex + ext
    path = os.path.join(UPLOAD_DIR, name)
    with open(path, "wb") as f:
        f.write(upload_file.file.read())
    return name

def create_report_zip(report_name: str, report_obj: dict, image_filenames: list):
    stamp = report_name
    report_dir = os.path.join(REPORTS_DIR, stamp)
    os.makedirs(report_dir, exist_ok=True)
    json_path = os.path.join(report_dir, "report.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(report_obj, fh, indent=2)
    for fn in image_filenames:
        src = os.path.join(UPLOAD_DIR, fn)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(report_dir, os.path.basename(src)))
    zip_path = os.path.join(REPORTS_DIR, f"{stamp}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(report_dir):
            for f in files:
                zf.write(os.path.join(root, f), arcname=f)
    return os.path.basename(zip_path)
