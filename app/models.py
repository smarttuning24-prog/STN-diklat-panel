from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Peserta(db.Model):
    __tablename__ = 'peserta'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=True)
    alamat = db.Column(db.String(255), nullable=True)
    nama_bengkel = db.Column(db.String(100), nullable=True)
    alamat_bengkel = db.Column(db.String(255), nullable=True)
    status_pekerjaan = db.Column(db.String(50), nullable=True)
    alasan = db.Column(db.Text, nullable=True)
    batch = db.Column(db.String(50), default="Batch Baru")
    akses_workshop = db.Column(db.Boolean, default=False)
    akses_dokumen_bengkel = db.Column(db.Boolean, default=False)  # Izin akses dokumen bengkel
    status_pembayaran = db.Column(db.String(20), default="Belum")  # "Belum", "Lunas", "Ditolak"
    whatsapp_link = db.Column(db.String(255), nullable=True)
    tanggal_daftar = db.Column(db.DateTime, default=datetime.utcnow)
    tanggal_izin_dokumen = db.Column(db.DateTime, nullable=True)  # Tanggal izin diberikan
    password_hash = db.Column(db.String(128), nullable=True)
    payment_proof = db.Column(db.String(255), nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

class Batch(db.Model):
    __tablename__ = 'batch'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False)
    whatsapp_link = db.Column(db.String(255), nullable=False)
    akses_workshop_default = db.Column(db.Boolean, default=False)
    aktif = db.Column(db.Boolean, default=True)
    tanggal_dibuat = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class DocumentAccess(db.Model):
    """Model untuk manage akses Dokumen Bengkel per group atau per individu"""
    __tablename__ = 'document_access'
    id = db.Column(db.Integer, primary_key=True)
    
    # Tipe akses: "group" atau "individual"
    tipe_akses = db.Column(db.String(20), nullable=False)  # "group" atau "individual"
    
    # Untuk akses group/batch
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=True)
    batch = db.relationship('Batch', backref='document_access')
    
    # Untuk akses individual
    peserta_id = db.Column(db.Integer, db.ForeignKey('peserta.id'), nullable=True)
    peserta = db.relationship('Peserta', backref='document_access')
    
    # Status akses
    akses_diberikan = db.Column(db.Boolean, default=True)
    tanggal_mulai = db.Column(db.DateTime, default=datetime.utcnow)
    tanggal_kadaluarsa = db.Column(db.DateTime, nullable=True)  # None = akses selamanya
    
    # Catatan dari admin
    catatan = db.Column(db.Text, nullable=True)
    
    # Metadata
    dibuat_oleh = db.Column(db.String(50), nullable=True)
    tanggal_dibuat = db.Column(db.DateTime, default=datetime.utcnow)
    tanggal_diubah = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_aktif(self):
        """Cek apakah akses masih aktif"""
        if not self.akses_diberikan:
            return False
        if self.tanggal_kadaluarsa:
            return datetime.utcnow() <= self.tanggal_kadaluarsa
        return True

class DocumentSyncLog(db.Model):
    """Log untuk tracking sinkronisasi Google Drive otomatis"""
    __tablename__ = 'document_sync_log'
    id = db.Column(db.Integer, primary_key=True)
    
    tanggal_sync = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)  # "success", "failed", "running"
    
    # Statistik sync
    folder_baru = db.Column(db.Integer, default=0)
    folder_update = db.Column(db.Integer, default=0)
    file_baru = db.Column(db.Integer, default=0)
    file_update = db.Column(db.Integer, default=0)
    
    # Detail error jika ada
    error_message = db.Column(db.Text, nullable=True)
    
    # Durasi sync
    durasi_detik = db.Column(db.Float, nullable=True)