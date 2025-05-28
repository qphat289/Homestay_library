from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
from flask_login import LoginManager

# Initialize extensions
cache = Cache()
limiter = Limiter(key_func=get_remote_address)
compress = Compress()
login_manager = LoginManager()

def init_extensions(app):
    """Initialize all Flask extensions"""
    # Configure Flask-Caching
    cache.init_app(app, config={
        'CACHE_TYPE': 'filesystem',
        'CACHE_DIR': 'cache',
        'CACHE_DEFAULT_TIMEOUT': 300,
        'CACHE_THRESHOLD': 1000,
        'CACHE_OPTIONS': {
            'mode': 0o600,
        }
    })

    # Configure rate limiter
    limiter.init_app(app)
    app.config['RATELIMIT_DEFAULT'] = "200 per day"
    app.config['RATELIMIT_STORAGE_URL'] = "memory://"

    # Configure compression
    compress.init_app(app)
    app.config['COMPRESS_MIMETYPES'] = [
        'text/html',
        'text/css',
        'text/xml',
        'application/json',
        'application/javascript',
        'image/svg+xml'
    ]
    app.config['COMPRESS_LEVEL'] = 6
    app.config['COMPRESS_MIN_SIZE'] = 500

    # Configure Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'login' 