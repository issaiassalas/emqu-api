from src import app
from src.routes.auth import auth_blueprint
from src.routes.device import device_blueprint
from src.routes.execution import execution_blueprint


app.register_blueprint(auth_blueprint, url_prefix="/api/auth/")
app.register_blueprint(device_blueprint, url_prefix="/api/")
app.register_blueprint(execution_blueprint, url_prefix="/api/")
