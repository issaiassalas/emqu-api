import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from src.config import DevelpmentConfig

app = Flask(__name__)

app_settings = os.getenv("APP_SETTINGS", DevelpmentConfig)
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
