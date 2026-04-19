from flask import Flask

from .config import Config
from .routes import register_routes


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)
    register_routes(app)
    return app
