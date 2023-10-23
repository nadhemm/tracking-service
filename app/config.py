import os
from decouple import config as load_env

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///dev.db"  # TODO: you probably need a better db for prod
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PARCELLAB_URL = load_env('PARCELLAB_URL')
    PARCELLAB_API_KEY = load_env('PARCELLAB_API_KEY')
    CELERY_BROKER_URL = load_env("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = load_env("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")


class TestConfig(Config):
    ENV_TYPE = "test"
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"


class LocalConfig(Config):
    ENV_TYPE = "local"


class DevelopmentConfig(Config):
    PARCELLAB_URL = "https://mock-api.parcellab.com"
    ENV_TYPE = "development"


class ProductionConfig(Config):
    PARCELLAB_URL = "https://api.parcellab.com"
    ENV_TYPE = "production"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "local": LocalConfig,
    "test": TestConfig,
}
