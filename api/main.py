from flask import Flask
from flask_restful import Api

from api.tools import add_app_resources_from


# TODO middleware - login required for some apps/paths.

def app_factory():
    app = Flask(__name__)
    api = Api(app)

    #: Adding the application tree into our Api.
    add_app_resources_from(api, "api.app")

    return app

app = app_factory()

if __name__ == "__main__":
    app.run(debug=True)
