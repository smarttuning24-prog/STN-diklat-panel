#!/usr/bin/env python3
"""
Versi Final: Sinkronisasi dua arah Google Drive ke database.
- Menyimpan parent_id, is_directory, mime_type
- Navigasi folder penuh di web
- Logging, lock file, SQLite/MySQL
- Hanya 4 folder target
"""

import os
import sys
import time
import tempfile
from datetime import datetime

# ============ Konfigurasi ============
USE_MYSQL = False  # Ubah ke True jika pakai MySQL

# SQLite
DB_PATH = "database.db"

# MySQL
MYSQL_CONFIG = {
    "host": "gazruxenginering.mysql.pythonanywhere-services.com",
    "user": "gazruxenginering",
    "password": "your_password",  # Ganti dengan password MySQL Anda
    "database": "gazruxenginering$default"
}

SERVICE_ACCOUNT_FILE = "credentials.json"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# Folder target: {key: folder_id}
TARGET_FOLDERS = {
    "EBOOKS": "12ffd7GqHAiy3J62Vu65LbVt6-ultog5Z",
    "Pengetahuan": "1Y2SLCbyHoB53BaQTTwRta2T6dv_drRll",
    "Service_Manual_1": "1CHz8UWZXfJtXlcjp9-FPAo-t_KkfTztW",
    "Service_Manual_2": "1_SsZ7SkaZxvXUZ6RUAA_o7WR_GAtgEwT"
}

LOCK_FILE = os.path.join(tempfile.gettempdir(), "sync_drive_advanced.lock")
LOG_FILE = f"sync_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

# ============ Logging ============
def log_message(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# ============ Lock File ============
def setup_lock():
    if os.path.exists(LOCK_FILE):
        log_message("🔒 Skrip sedang berjalan. Keluar.")
        sys.exit(1)
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    def cleanup():
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    import atexit
    atexit.register(cleanup)

# ============ Database Manager ============
class DatabaseManager:
    def __init__(self, use_mysql=False):
        self.use_mysql = use_mysql
        if use_mysql:
            import pymysql
            self.conn = pymysql.connect(**MYSQL_CONFIG)
        else:
            import sqlite3
            self.conn = sqlite3.connect(DB_PATH)

    def execute(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def create_table(self):
        if self.use_mysql:
            q = """
            CREATE TABLE IF NOT EXISTS files (
                id VARCHAR(255) PRIMARY KEY,
                name TEXT,
                is_directory BOOLEAN DEFAULT 0,
                size BIGINT DEFAULT 0,
                modified_time DATETIME,
                parent_id VARCHAR(255),
                root_folder_name VARCHAR(255),
                mime_type TEXT
            ) ENGINE=InnoDB;
            """
        else:
            q = """
            CREATE TABLE IF NOT EXISTS files (
                id TEXT PRIMARY KEY,
                name TEXT,
                is_directory BOOLEAN DEFAULT 0,
                size INTEGER DEFAULT 0,
                modified_time TEXT,
                parent_id TEXT,
                root_folder_name TEXT,
                mime_type TEXT
            )
            """
        self.execute(q)
        self.commit()

    def get_all_ids(self):
        cursor = self.execute("SELECT id FROM files")
        return set(row[0] for row in cursor.fetchall())

    def insert_or_update(self, item):
        if self.use_mysql:
            q = """
            INSERT INTO files 
            (id, name, is_directory, modified_time, parent_id, root_folder_name, mime_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                is_directory = VALUES(is_directory),
                modified_time = VALUES(modified_time),
                parent_id = VALUES(parent_id),
                root_folder_name = VALUES(root_folder_name),
                mime_type = VALUES(mime_type)
            """
        else:
            q = """
            INSERT OR REPLACE INTO files
            (id, name, is_directory, modified_time, parent_id, root_folder_name, mime_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
        self.execute(q, (
            item['id'],
            item['name'],
            item['is_directory'],
            item['modified_time'],
            item.get('parent_id'),
            item['root_folder_name'],
            item.get('mime_type', '')
        ))

    def delete_by_ids(self, ids_to_delete):
        if not ids_to_delete:
            return
        placeholders = ','.join(['%s'] if self.use_mysql else ['?' for _ in ids_to_delete])
        q = f"DELETE FROM files WHERE id IN ({placeholders})"
        self.execute(q, list(ids_to_delete))

# ============ Google Drive ============
def get_credentials():
    from google.oauth2.service_account import Credentials as SAC
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"File {SERVICE_ACCOUNT_FILE} tidak ditemukan.")
    creds = SAC.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    log_message("✅ Service Account berhasil dimuat.")
    return creds

def list_files_recursive(service, folder_id, root_name, current_parent_id):
    items = []
    page_token = None
    query = f"'{folder_id}' in parents"

    while True:
        res = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, parents)",
            pageToken=page_token,
            pageSize=1000
        ).execute()

        for item in res.get('files', []):
            parents = item.get('parents', [folder_id])
            actual_parent = parents[0]
            is_dir = item['mimeType'] == 'application/vnd.google-apps.folder'

            entry = {
                'id': item['id'],
                'name': item['name'],
                'modified_time': item['modifiedTime'],
                'parent_id': actual_parent,
                'root_folder_name': root_name,
                'is_directory': 1 if is_dir else 0,
                'mime_type': item.get('mimeType', '')
            }

            items.append(entry)

            if is_dir:
                items.extend(list_files_recursive(service, item['id'], root_name, actual_parent))

        page_token = res.get('nextPageToken')
        if not page_token:
            break

    return items

def get_drive_files(service):
    log_message("📥 Memindai 4 folder target di Google Drive...")
    all_items = []
    drive_ids = set()

    for key, folder_id in TARGET_FOLDERS.items():
        log_message(f"  → Folder: {key}")
        items = list_files_recursive(service, folder_id, key, folder_id)
        log_message(f"    ➤ {len(items)} item ditemukan (file + folder)")
        for it in items:
            if it['id'] not in drive_ids:
                drive_ids.add(it['id'])
                all_items.append(it)
            else:
                log_message(f"⚠️ Duplikat ID: {it['id']}")

    log_message(f"✅ Total item unik: {len(all_items)}")
    return all_items, drive_ids

# ============ Main ============
def main():
    start_time = time.time()
    log_message("="*50)
    log_message("🚀 Memulai sinkronisasi dua arah Google Drive...")

    setup_lock()

    try:
        db = DatabaseManager(use_mysql=USE_MYSQL)
        db.create_table()

        from googleapiclient.discovery import build
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)

        drive_items, drive_ids = get_drive_files(service)

        log_message("💾 Menyinkronkan ke database...")
        for item in drive_items:
            db.insert_or_update(item)

        db_ids = db.get_all_ids()
        to_delete = db_ids - drive_ids
        db.delete_by_ids(to_delete)

        db.commit()
        db.close()

        updated = len(drive_items)
        deleted = len(to_delete)
        log_message(f"📊 Ringkasan: {updated} item disinkron, {deleted} dihapus dari DB.")
        log_message(f"⏱️  Selesai dalam {time.time() - start_time:.1f} detik.")
        log_message("🎉 Sinkronisasi dua arah berhasil!")

    except Exception as e:
        log_message(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()