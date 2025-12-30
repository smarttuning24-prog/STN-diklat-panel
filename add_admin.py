from app import create_app
from app.models import db, Admin

app = create_app()
with app.app_context():
    admin = Admin(username="admin")  # ✅ Admin model fields
    admin.set_password("admin123")
    if not Admin.query.filter_by(username="admin").first():
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin dibuat: Username=admin, Password=admin123")
    else:
        print("⚠️ Admin sudah ada.")