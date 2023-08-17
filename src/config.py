import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_STRING_CONNECTION = "sqlite:///"
DATABASE_NAME = os.getenv("DB_NAME", "emqu_api.db")


class BaseConfig:
    "Base configuration"
    SECRET_KEY = os.getenv("SECRET_KEY", "SECRET_KEY")
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelpmentConfig(BaseConfig):
    """Development configuration"""

    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = DATABASE_STRING_CONNECTION + DATABASE_NAME
