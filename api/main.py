from flask import Flask
from flask_restful import Api

from api.tools import add_resources_from


if __name__ == "__main__":
    app = Flask(__name__)
    api = Api(app)

    #: Adding the application tree into our Api.
    add_resources_from(api, "api.app")

    app.run(debug=True)
