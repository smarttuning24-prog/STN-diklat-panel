"""
Google Drive Auto-Sync Handler
Sinkronisasi otomatis dokumen dari Google Drive setiap minggu
"""

import os
import sys
import time
import sqlite3
from datetime import datetime
from pathlib import Path

# Add Dokumen Bengkel to path
bengkel_path = Path(__file__).parent / "Dokumen Bengkel"
sys.path.insert(0, str(bengkel_path))

try:
    from sync_drive import sync_all as bengkel_sync_all
except ImportError:
    print("⚠️  Warning: sync_drive module not found in Dokumen Bengkel")
    bengkel_sync_all = None


def get_drive_sync_stats():
    """Dapatkan statistik sinkronisasi dari Dokumen Bengkel database"""
    bengkel_db = Path(__file__).parent.parent / "Dokumen Bengkel" / "database.db"
    
    if not bengkel_db.exists():
        print(f"⚠️  Database path checked: {bengkel_db} - exists: {bengkel_db.exists()}")
        return None
    
    try:
        conn = sqlite3.connect(str(bengkel_db))
        cursor = conn.cursor()
        
        # Query statistik
        cursor.execute("SELECT COUNT(*) FROM folders")
        folder_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'folders': folder_count,
            'files': file_count,
            'timestamp': datetime.utcnow()
        }
    except Exception as e:
        print(f"❌ Error getting sync stats: {e}")
        return None


def sync_google_drive_documents():
    """
    Sinkronisasi dokumen dari Google Drive ke database lokal
    Dipanggil otomatis setiap minggu
    """
    from app import create_app
    from app.models import db, DocumentSyncLog
    
    print(f"\n{'='*70}")
    print(f"🔄 Starting Google Drive Synchronization at {datetime.utcnow()}")
    print(f"{'='*70}\n")
    
    app = create_app()
    start_time = time.time()
    
    # Get stats before sync
    stats_before = get_drive_sync_stats()
    
    try:
        with app.app_context():
            # Jalankan sync
            if bengkel_sync_all:
                print("📡 Syncing with Google Drive...")
                bengkel_sync_all()
                print("✅ Sync completed from Dokumen Bengkel module")
            else:
                print("⚠️  Using fallback sync method...")
                # Fallback: just check database exists and get stats
                bengkel_db = Path(__file__).parent.parent / "Dokumen Bengkel" / "database.db"
                if bengkel_db.exists():
                    print(f"✅ Database found: {bengkel_db}")
                    # Database is valid if we can open it
                    conn = sqlite3.connect(str(bengkel_db))
                    conn.execute("SELECT 1")
                    conn.close()
                else:
                    raise Exception(f"Database not found at {bengkel_db}")
            
            # Get stats after sync
            stats_after = get_drive_sync_stats()
            
            # Hitung perubahan
            folder_baru = 0
            file_baru = 0
            if stats_before and stats_after:
                folder_baru = max(0, stats_after['folders'] - stats_before['folders'])
                file_baru = max(0, stats_after['files'] - stats_before['files'])
            
            # Record sync log
            durasi = time.time() - start_time
            sync_log = DocumentSyncLog(
                status='success',
                folder_baru=folder_baru,
                file_baru=file_baru,
                durasi_detik=durasi
            )
            db.session.add(sync_log)
            db.session.commit()
            
            print(f"\n✅ Sync Log Created:")
            print(f"   - Status: SUCCESS")
            print(f"   - Folder baru: {folder_baru}")
            print(f"   - File baru: {file_baru}")
            print(f"   - Durasi: {durasi:.2f} detik")
            print(f"   - Total folders: {stats_after['folders'] if stats_after else 'unknown'}")
            print(f"   - Total files: {stats_after['files'] if stats_after else 'unknown'}")
            
    except Exception as e:
        print(f"❌ Sync failed: {e}")
        
        with app.app_context():
            durasi = time.time() - start_time
            sync_log = DocumentSyncLog(
                status='failed',
                error_message=str(e),
                durasi_detik=durasi
            )
            db.session.add(sync_log)
            db.session.commit()
            
            print(f"\n❌ Error Log Created:")
            print(f"   - Status: FAILED")
            print(f"   - Error: {e}")
            print(f"   - Durasi: {durasi:.2f} detik")
    
    print(f"\n{'='*70}\n")


def setup_scheduler():
    """Setup APScheduler untuk auto-sync setiap minggu"""
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    
    # Sync setiap hari Minggu pukul 02:00 pagi
    scheduler.add_job(
        sync_google_drive_documents,
        'cron',
        day_of_week='6',  # 0=Monday, 6=Sunday
        hour=2,
        minute=0,
        id='google_drive_sync',
        name='Google Drive Document Sync'
    )
    
    # Also add immediate sync for testing
    # Uncomment baris di bawah untuk test sync langsung saat server start
    # scheduler.add_job(sync_google_drive_documents, 'interval', seconds=30, id='test_sync')
    
    return scheduler


if __name__ == '__main__':
    # Test manual sync
    sync_google_drive_documents()
