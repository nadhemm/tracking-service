import os

from celery import Celery
from flask import Flask
from flask_cors import CORS
# from flask_sqlalchemy import Model, SQLAlchemy

from app.config import config, Config
# from app.models import db
# from flask_migrate import Migrate

celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, backend=Config.CELERY_RESULT_BACKEND)


# class DefaultModel(Model):
#     def add(self, auto_commit: bool = False):
#         db.session.add(self)
#         if auto_commit:
#             db.session.commit()
#         return self

# BaseModel = db.Model

# db = SQLAlchemy(
#     model_class=DefaultModel, # session_options={"autoflush": False},
# )
# migrate = Migrate()


def create_app(env):
    app = Flask(__name__)

    CORS(app, origins="*", supports_credentials=True)

    config_name = env
    app.config.from_object(config[config_name])

    from app.models import db
    db.init_app(app)
    # migrate.init_app(app, db)
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    from . import models
    from app.api import rest as rest_blueprint

    app.register_blueprint(rest_blueprint, url_prefix="/rest")

    return app


app = create_app(os.getenv("FLASK_CONFIG") or "local")
