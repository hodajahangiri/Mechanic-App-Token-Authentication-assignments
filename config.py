class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///mechanic_app.db'
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 200
    

class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing_mechanic_app.db'
    DEBUG = True
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300
    TESTING = True


class ProductionConfig:
    pass