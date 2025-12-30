import os
import json
import time
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# ID folder Google Drive Anda
FOLDERS = {
    "EBOOKS": "12ffd7GqHAiy3J62Vu65LbVt6-ultog5Z",
    "pengetahuan": "1Y2SLCbyHoB53BaQTTwRta2T6dv_drRll",
    "service_manual_1": "1CHz8UWZXfJtXlcjp9-FPAo-t_KkfTztW",
    "service_manual_2": "1_SsZ7SkaZxvXUZ6RUAA_o7WR_GAtgEwT"
}

# ✅ Add caching
CACHE_DIR = 'instance/cache'
CACHE_FILE = os.path.join(CACHE_DIR, 'docs_catalog_cache.json')
CACHE_DURATION = 3600  # 1 hour

def get_cached_catalog():
    """Get catalog from cache if fresh"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            if time.time() - data.get('timestamp', 0) < CACHE_DURATION:
                return data.get('catalog'), True  # Return cache
    return None, False

def save_catalog_cache(catalog):
    """Save catalog to cache"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_FILE, 'w') as f:
        json.dump({
            'timestamp': time.time(),
            'catalog': catalog
        }, f)

def get_drive_service():
    if not os.path.exists('credentials.json'):
        raise FileNotFoundError("❌ File 'credentials.json' tidak ditemukan!")
    creds = service_account.Credentials.from_service_account_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    return build('drive', 'v3', credentials=creds)

def list_files(service, folder_id):
    files = []
    page_token = None
    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, size, mimeType)",
            pageSize=1000,
            pageToken=page_token
        ).execute()
        for f in response.get('files', []):
            if f['mimeType'] != 'application/vnd.google-apps.folder':
                size_mb = round(int(f.get('size', 0)) / (1024**2), 2) if 'size' in f else 0
                files.append({
                    "name": f['name'],
                    "file_id": f['id'],
                    "size_mb": size_mb
                })
        page_token = response.get('nextPageToken')
        if not page_token: break
    return files

def main():
    # ✅ Check cache first
    cached_catalog, from_cache = get_cached_catalog()
    if from_cache:
        print("📦 Using cached catalog (< 1 hour old)")
        return cached_catalog
    
    print("🚀 Fetching fresh catalog from Google Drive...")
    service = get_drive_service()
    catalog = {}
    total_files = 0

    for name, fid in FOLDERS.items():
        print(f"  → Mengambil {name}...")
        files = list_files(service, fid)
        catalog[name] = files
        total_files += len(files)
        print(f"    ✅ {len(files)} file ditemukan")

    os.makedirs('static', exist_ok=True)
    with open('static/docs_catalog.json', 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    # ✅ Save to cache
    save_catalog_cache(catalog)

    print(f"\n✅ Verifikasi selesai! Total: {total_files} file")
    print("📁 File tersimpan di: static/docs_catalog.json")

if __name__ == '__main__':
    main()