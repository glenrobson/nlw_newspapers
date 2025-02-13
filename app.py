from flask import Flask
from config.config import Config
from importer import importRoute
from view import viewRoutes

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Blueprints
    app.register_blueprint(importRoute.import_blueprint)
    app.register_blueprint(viewRoutes.view_blueprint)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
