import secrets

import bcrypt
from flask import request, url_for
from flask_restful import Api, Resource

from db.manager import manager as dbman


AUTH_ROOT_PATH = "/accounts"


class Auth:
    def __init__(self, app):
        self.api = Api(app)

        self.api.add_resource(_Accounts, _Accounts.PATH)
        self.api.add_resource(_LogIn, _LogIn.PATH)
        self.api.add_resource(_LogOut, _LogOut.PATH)

        self.sub_apps = []


class _Accounts(Resource):
    PATH = "/".join([AUTH_ROOT_PATH])

    def get(self):
        return {
            "_links": {
                "self": {"href": self.PATH},
                "curies": [{"name": "auth", "href": "TODO/{rel}", "templated": True}],
                "auth:login": {"href": _LogIn.PATH, "templated": True},
                "auth:logout": {"href": _LogOut.PATH, "templated": True},
            }
        }


class _LogIn(Resource):
    PATH = "/".join([AUTH_ROOT_PATH, "login"])

    def post(self):

        cpf = request.form.get("cpf")
        password = request.form.get("password")

        if not isinstance(cpf, str):
            raise Exception
        if not isinstance(password, str):
            raise Exception

        target_user = dbman.auth.get_user(cpf=cpf)
        if not bcrypt.checkpw(
            password.encode("utf-8"), target_user.password.encode("utf-8")
        ):
            raise Exception

        session_token = None
        while session_token is None:
            session, created = dbman.auth.create_session(
                target_user, secrets.token_hex(64)
            )
            if created:
                session_token = session.token
        return {"_links": {"self": {"href": self.PATH}}, "token": session_token}


class _LogOut(Resource):
    PATH = "/".join([AUTH_ROOT_PATH, "logout"])

    def post(self):

        session_token = request.form.get("Authentication")
        if not isinstance(session_token, str):
            raise Exception

        return {
            "_links": {
                "self": {"href": self.PATH},
                "curies": [{"name": "rd", "href": "TODO/{rel}", "templated": True}],
                "rd:index": {"href": url_for("_index"), "templated": True},
            },
            "logged_out": dbman.auth.expire_session(session_token),
        }
