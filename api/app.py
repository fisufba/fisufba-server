from flask import Flask
from flask_restful import Api, Resource

from api.auth import Auth, AUTH_ROOT_PATH


APP_ROOT_PATH = "/"


class App:
    def __init__(self, app):
        self.api = Api(app)

        self.api.add_resource(_Index, _Index.PATH)

        self.sub_apps = [Auth(app)]


class _Index(Resource):
    PATH = APP_ROOT_PATH

    def get(self):
        return {
            "_links": {
                "self": {"href": self.PATH},
                "curies": [{"name": "auth", "href": "TODO/{rel}", "templated": True}],
                "auth:accounts": {"href": AUTH_ROOT_PATH, "templated": True},
            }
        }


def main():
    app = Flask(__name__)

    # TODO middleware - login required for some apps/paths.
    apps = [App(app)]

    app.run(debug=True)


if __name__ == "__main__":
    main()
