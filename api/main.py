from flask import Flask
from flask_restful import Api

from utils.api import add_resources_from


if __name__ == "__main__":
    app = Flask(__name__)
    api = Api(app)

    # TODO middleware - login required for some apps/paths.
    add_resources_from(api, "api.app")

    app.run(debug=False)
