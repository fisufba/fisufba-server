import secrets

import bcrypt
from flask import request, url_for

from utils.api import AppResource
from db.manager import manager as dbman


class _Accounts(AppResource):
    @classmethod
    def get_path(cls):
        return "/accounts"

    @classmethod
    def get_dependencies(cls):
        return set()

    def get(self):
        return {"_links": {"self": {"href": self.get_path()}}}


class _LogIn(AppResource):
    @classmethod
    def get_path(cls):
        return "/accounts/login"

    @classmethod
    def get_dependencies(cls):
        return set()

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
        return {"_links": {"self": {"href": self.get_path()}}, "token": session_token}


class _LogOut(AppResource):
    @classmethod
    def get_path(cls):
        return "/accounts/logout"

    @classmethod
    def get_dependencies(cls):
        return set()

    def post(self):

        session_token = request.form.get("Authentication")
        if not isinstance(session_token, str):
            raise Exception

        return {
            "_links": {
                "self": {"href": self.get_path()},
                "curies": [{"name": "rd", "href": "TODO/{rel}", "templated": True}],
                "rd:index": {"href": url_for("_index"), "templated": True},
            },
            "logged_out": dbman.auth.expire_session(session_token),
        }
