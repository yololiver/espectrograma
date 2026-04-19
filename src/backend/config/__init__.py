import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = os.environ.get("DEBUG", "1") == "1"
