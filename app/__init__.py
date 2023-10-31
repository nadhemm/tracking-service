import os

from celery import Celery
from flask import Flask
from flask_cors import CORS

from app.config import config, Config
from app.models import db

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)


def create_app(env):
    app = Flask(__name__)

    CORS(app, origins="*", supports_credentials=True)

    config_name = env
    app.config.from_object(config[config_name])

    from app.models import db
    db.init_app(app)
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    from . import models
    from app.apis.tracking import rest as rest_blueprint

    app.register_blueprint(rest_blueprint, url_prefix="/rest")

    from app.errors import InvalidInputData
    from flask import jsonify
    @app.errorhandler(InvalidInputData)
    def handle_invalid_input_data(error):
        response = jsonify({"error": str(error)})
        response.status_code = error.status_code
        return response

    return app


app = create_app(os.getenv("FLASK_CONFIG") or "local")
