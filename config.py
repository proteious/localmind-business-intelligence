import os

# Foursquare API Configuration
FOURSQUARE_API_KEY = os.environ.get('FOURSQUARE_API_KEY', 'your_foursquare_api_key_here')

# Flask Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = True

# Business Intelligence Settings
DEFAULT_SEARCH_RADIUS = 1000  # meters
MAX_COMPETITORS = 20
BUSINESS_CATEGORIES = {
    'restaurant': 'Food & Dining',
    'retail': 'Retail & Shopping',
    'fitness': 'Fitness & Recreation',
    'beauty': 'Beauty & Personal Care',
    'professional': 'Professional Services',
    'healthcare': 'Healthcare',
    'education': 'Education'
}

# Additional Configuration Settings
API_TIMEOUT = 30  # seconds
MAX_SEARCH_RADIUS = 5000  # meters
MIN_SEARCH_RADIUS = 100  # meters

# Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/localmind.log'

class Config:
    """Configuration class for LocalMind Business Intelligence Agent"""
    
    # Flask Configuration
    SECRET_KEY = SECRET_KEY
    DEBUG = DEBUG
    
    # API Keys
    FOURSQUARE_API_KEY = FOURSQUARE_API_KEY
    
    # Business Intelligence Settings
    DEFAULT_SEARCH_RADIUS = DEFAULT_SEARCH_RADIUS
    MAX_SEARCH_RADIUS = MAX_SEARCH_RADIUS
    MIN_SEARCH_RADIUS = MIN_SEARCH_RADIUS
    MAX_COMPETITORS = MAX_COMPETITORS
    BUSINESS_CATEGORIES = BUSINESS_CATEGORIES
    
    # API Configuration
    API_TIMEOUT = API_TIMEOUT
    
    # Logging
    LOG_LEVEL = LOG_LEVEL
    LOG_FILE = LOG_FILE
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Enhanced security for production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production")
    
    FOURSQUARE_API_KEY = os.environ.get('FOURSQUARE_API_KEY')
    if not FOURSQUARE_API_KEY:
        raise ValueError("No FOURSQUARE_API_KEY set for production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use mock data for testing
    FOURSQUARE_API_KEY = 'test-api-key'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}