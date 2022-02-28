from flask import Flask
from flask_redis import FlaskRedis
from flask_mongoengine import MongoEngine

from fakeredis import FakeStrictRedis
from redis import StrictRedis

from dotenv import load_dotenv
import os

try:
    from api.homma.routes.datafile_routes import datafile_routes
    from api.homma.routes.session_routes import session_routes
except:
    from .api.homma.routes.datafile_routes import datafile_routes
    from .api.homma.routes.session_routes import session_routes

load_dotenv()
content_folder = os.environ.get("CONTENT_FOLDER", None)
if "~" in content_folder:
    os.environ["CONTENT_FOLDER"] = content_folder.replace("~", os.path.expanduser("~"))


def create_app(
    name: str = __name__,
    db_config: dict = {"db": "homma", "host": "mongodb://127.0.0.1:27017/homma"},
    redis_url: str = "redis://127.0.0.1:6379",
    testing: bool = False,
) -> Flask:

    app = Flask(name)
    db = MongoEngine()
    redis_client = None
    if not testing:
        redis_client = FlaskRedis.from_custom_provider(StrictRedis)
    else:
        redis_client = FlaskRedis.from_custom_provider(FakeStrictRedis)
    app.config.update(
        SECRET_KEY=os.environ["SECRET_KEY"],
        TESTING=testing,
        MONGODB_SETTINGS=db_config,
        REDIS_URL=redis_url,
    )
    app.register_blueprint(session_routes)
    app.register_blueprint(datafile_routes)
    redis_client.init_app(app)
    db.init_app(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
