from flask import Flask
import os
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Environment detection
    is_development = os.getenv('FLASK_ENV') == 'development' or app.config.get('DEBUG', False)
    is_codespaces = 'GITHUB_CODESPACES_PORT' in os.environ
    is_production = not is_development and not is_codespaces

    print(f"Environment: {'Development' if is_development else 'Codespaces' if is_codespaces else 'Production'}")

    # SECRET_KEY configuration
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        if is_production:
            raise ValueError("SECRET_KEY environment variable is required in production!")
        else:
            secret_key = 'dev-secret-key-change-in-production-' + str(os.getpid())
            print("⚠️  Using development SECRET_KEY - set SECRET_KEY environment variable for production")

    app.config['SECRET_KEY'] = secret_key

    # Database configuration
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'users.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Upload configuration
    upload_folder = os.path.join(os.path.dirname(__file__), '..', 'instance', 'uploads')
    upload_folder = os.path.abspath(upload_folder)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024  # 8 MB

    # API Keys Configuration (for offline/API access without CSRF)
    api_keys = os.getenv('API_KEYS', 'offline-dev-key-123').split(',')
    app.config['VALID_API_KEYS'] = [key.strip() for key in api_keys]
    app.config['IP_WHITELIST'] = [ip.strip() for ip in os.getenv('IP_WHITELIST', '127.0.0.1,localhost').split(',')]

    # CSRF Protection - can be disabled with WTF_CSRF_ENABLED=False
    csrf_enabled = os.getenv('WTF_CSRF_ENABLED', 'True').lower() != 'false'
    app.config['WTF_CSRF_ENABLED'] = csrf_enabled
    
    if csrf_enabled:
        print("✅ CSRF Protection: ENABLED")
    else:
        print("⚠️  CSRF Protection: DISABLED (Development/Testing only)")

    csrf = CSRFProtect(app)

    # CSRF exemption handler - bypass for API keys or localhost
    @csrf.exempt
    def csrf_exempt_for_api():
        from .security import is_csrf_exempted
        if is_csrf_exempted():
            return True
        return False

    # Rate limiting
    from .security import init_limiter
    init_limiter(app)

    # Database initialization
    from .models import db
    db.init_app(app)

    with app.app_context():
        # Ensure upload folder exists
        try:
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        except Exception as e:
            print(f"Warning: Could not create upload folder: {e}")

        db.create_all()

    # CSP Configuration based on environment
    @app.after_request
    def add_security_headers(response):
        # CSP based on environment
        if is_codespaces:
            # GitHub Codespaces: Allow unsafe-eval for compatibility
            csp = "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;"
        elif is_production:
            # Production: Strict CSP
            csp = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self';"
        else:
            # Development: Permissive for debugging
            csp = "default-src 'self'; script-src 'self' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:;"

        response.headers['Content-Security-Policy'] = csp

        # Additional security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        return response

    from .routes import main
    app.register_blueprint(main)

    # Setup scheduler untuk auto-sync Google Drive
    try:
        from .drive_sync import setup_scheduler
        scheduler = setup_scheduler()
        scheduler.start()
        print("✅ Google Drive Auto-Sync: SCHEDULED (setiap Minggu pukul 02:00)")
    except Exception as e:
        print(f"⚠️  Could not setup scheduler: {e}")

    return app