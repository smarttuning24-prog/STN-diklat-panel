#!/usr/bin/env python3
"""
STN Diklat Panel - Flask Application Runner

Supports multiple deployment environments:
- Development (local)
- GitHub Codespaces
- Production (server)

Usage:
    python run.py                    # Auto-detect environment
    FLASK_ENV=development python run.py
    FLASK_ENV=production python run.py
"""

from app import create_app
import os
import sys

def main():
    app = create_app()

    # Environment detection
    is_codespaces = 'GITHUB_CODESPACES_PORT' in os.environ
    is_production = os.getenv('FLASK_ENV') == 'production'
    is_development = os.getenv('FLASK_ENV') == 'development' or not is_production

    # Port configuration
    if is_codespaces:
        # GitHub Codespaces provides port via environment
        port = int(os.environ.get('GITHUB_CODESPACES_PORT', 8080))
        host = '0.0.0.0'
        print(f"🚀 Starting in GitHub Codespaces mode on port {port}")
    elif is_production:
        # Production server
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        debug = False
        print(f"🚀 Starting in Production mode on {host}:{port}")
    else:
        # Development
        host = os.getenv('HOST', '127.0.0.1')
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('DEBUG', 'True').lower() == 'true'
        print(f"🚀 Starting in Development mode on {host}:{port} (debug={debug})")

    # Check for required environment variables in production
    if is_production and not os.getenv('SECRET_KEY'):
        print("❌ ERROR: SECRET_KEY environment variable is required in production!")
        print("   Set it with: export SECRET_KEY='your-secret-key-here'")
        sys.exit(1)

    # Start server
    try:
        print(f"🌐 Server will be available at: http://{host}:{port}")
        print(f"📊 Environment: {'Production' if is_production else 'Codespaces' if is_codespaces else 'Development'}")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)

        app.run(
            host=host,
            port=port,
            debug=debug if not is_production else False,
            use_reloader=debug and not is_codespaces,  # Disable reloader in Codespaces
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()