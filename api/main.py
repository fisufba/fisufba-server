from flask import Flask
from flask_restful import Api

from api.tools import add_resources_from


def app_factory():
    app = Flask(__name__)
    api = Api(app)

    #: Adding the application tree into our Api.
    add_resources_from(api, "api.app")

    return app


def add_cors_to_response(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers[
        "Access-Control-Allow-Methods"
    ] = "OPTIONS, GET, POST, PUT, PATCH, DELETE"
    return response


app = app_factory()

if __name__ == "__main__":

    # Allow Cross-Origin requests only for debugging!
    # Production builds should live under the same domain as the frontend.
    app.after_request(add_cors_to_response)

    app.run(debug=True)
