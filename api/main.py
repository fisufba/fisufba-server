from flask import Flask
from flask_restful import Api

from api.tools import add_app_resources_from


# TODO middleware - login required for some apps/paths.

if __name__ == "__main__":
    app = Flask(__name__)
    api = Api(app)

    #: Adding the application tree into our Api.
    add_app_resources_from(api, "api.app")

    app.run(debug=True)

    Exception
