"""
Handler untuk Dokumen Bengkel
Mengintegrasikan sinkronisasi Google Drive dengan database lokal
"""

import os
import sqlite3
import json
from pathlib import Path

# Konfigurasi Root Folder (sesuai dengan Dokumen Bengkel/app.py)
ROOT_FOLDERS = {
    "EBOOKS": "12ffd7GqHAiy3J62Vu65LbVt6-ultog5Z",
    "Pengetahuan": "1Y2SLCbyHoB53BaQTTwRta2T6dv_drRll",
    "Service_Manual_1": "1CHz8UWZXfJtXlcjp9-FPAo-t_KkfTztW",
    "Service_Manual_2": "1_SsZ7SkaZxvXUZ6RUAA_o7WR_GAtgEwT"
}

DISPLAY_NAMES = {
    "EBOOKS": "📚 EBOOKS",
    "Pengetahuan": "🧠 Pengetahuan",
    "Service_Manual_1": "🔧 Service Manual (1)",
    "Service_Manual_2": "⚙️ Service Manual (2)"
}


def get_documents_db_path():
    """Dapatkan path database Dokumen Bengkel"""
    bengkel_dir = Path(__file__).parent.parent / "Dokumen Bengkel"
    db_path = bengkel_dir / "database.db"
    return str(db_path)


def get_documents_connection():
    """Koneksi ke database Dokumen Bengkel"""
    db_path = get_documents_db_path()
    if not os.path.exists(db_path):
        # Log warning and return None so callers can handle missing DB
        print(f"⚠️  Dokumen Bengkel database tidak ditemukan di: {db_path}")
        return None

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"❌ Gagal membuka database Dokumen Bengkel: {e}")
        return None


def safe_get(row, key, default=None):
    """Safely get value from sqlite3.Row"""
    try:
        return row[key] if key in row.keys() else default
    except:
        return default


def sizeof_fmt(num, suffix="B"):
    """Format ukuran file"""
    if not num or num == "—":
        return "—"
    try:
        num = int(num)
    except:
        return "—"
    for unit in ["", "K", "M", "G"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} T{suffix}"


def get_root_list():
    """Ambil daftar root folders dengan jumlah file"""
    conn = get_documents_connection()
    if not conn:
        return []
    
    try:
        root_list = []
        for key, folder_id in ROOT_FOLDERS.items():
            count = conn.execute(
                "SELECT COUNT(*) FROM files WHERE (parent_id = ?) OR (root_folder_name = ?)",
                (folder_id, key)
            ).fetchone()[0]
            name = DISPLAY_NAMES.get(key, key)
            root_list.append({
                'name': name,
                'folder_id': folder_id,
                'count': count,
                'key': key
            })
        return root_list
    finally:
        conn.close()


def get_folder_contents(folder_id):
    """Ambil isi folder berdasarkan folder_id"""
    conn = get_documents_connection()
    if not conn:
        return None, None
    
    try:
        # Cari nama folder
        folder_name = "Folder"
        for key, fid in ROOT_FOLDERS.items():
            if fid == folder_id:
                folder_name = DISPLAY_NAMES.get(key, key)
                break
        else:
            folder_row = conn.execute(
                "SELECT name FROM files WHERE id = ? AND is_directory = 1", (folder_id,)
            ).fetchone()
            if folder_row:
                folder_name = folder_row['name']
        
        # Ambil items dalam folder
        items = conn.execute(
            "SELECT * FROM files WHERE parent_id = ? ORDER BY is_directory DESC, name",
            (folder_id,)
        ).fetchall()
        
        # Konversi ke dict untuk template
        items_list = []
        for item in items:
            items_list.append({
                'id': item['id'],
                'name': item['name'],
                'is_directory': item['is_directory'],
                'mime_type': safe_get(item, 'mime_type', ''),
                'size': sizeof_fmt(safe_get(item, 'size', 0)),
                'file_id': item['id']
            })
        
        return folder_name, items_list
    finally:
        conn.close()


def get_file_info(file_id):
    """Ambil info file untuk preview"""
    conn = get_documents_connection()
    if not conn:
        return None
    
    try:
        file = conn.execute(
            "SELECT * FROM files WHERE id = ? AND is_directory = 0", (file_id,)
        ).fetchone()
        
        if not file:
            return None
        
        return {
            'id': file['id'],
            'name': file['name'],
            'mime_type': safe_get(file, 'mime_type', ''),
            'size': sizeof_fmt(safe_get(file, 'size', 0)),
            'parent_id': safe_get(file, 'parent_id', ''),
            'root_folder_name': safe_get(file, 'root_folder_name', '')
        }
    finally:
        conn.close()


def search_files(query):
    """Cari file berdasarkan query"""
    if not query or len(query.strip()) < 2:
        return []
    
    conn = get_documents_connection()
    if not conn:
        return []
    
    try:
        results = conn.execute(
            "SELECT * FROM files WHERE name LIKE ? ORDER BY root_folder_name, name LIMIT 50",
            (f"%{query}%",)
        ).fetchall()
        
        results_list = []
        for r in results:
            results_list.append({
                'id': r['id'],
                'name': r['name'],
                'is_directory': r['is_directory'],
                'mime_type': safe_get(r, 'mime_type', ''),
                'root_folder_name': safe_get(r, 'root_folder_name', ''),
                'parent_id': safe_get(r, 'parent_id', '')
            })
        
        return results_list
    finally:
        conn.close()


def get_documents_catalog():
    """Ambil katalog dokumentasi lengkap per kategori"""
    conn = get_documents_connection()
    if not conn:
        return {}
    
    try:
        catalog = {}
        
        for key, folder_id in ROOT_FOLDERS.items():
            display_name = DISPLAY_NAMES.get(key, key)
            
            # Ambil files langsung di folder root
            files = conn.execute(
                "SELECT * FROM files WHERE parent_id = ? AND is_directory = 0 ORDER BY name",
                (folder_id,)
            ).fetchall()
            
            catalog[display_name] = [
                {
                    'name': f['name'],
                    'file_id': f['id'],
                    'size_mb': f['size'] // (1024 * 1024) if f['size'] else 0,
                    'mime_type': f['mime_type'] if f['mime_type'] else ''
                }
                for f in files
            ]
        
        return catalog
    finally:
        conn.close()
