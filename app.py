from src import app, db, models, routes
from flask_migrate import Migrate

migrate = Migrate(app, db)
