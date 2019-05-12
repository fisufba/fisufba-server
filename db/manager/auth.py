import datetime

import peewee

from utils.utils import is_valid_cpf
from db.models.auth import User, Session


class Auth:
    def __init__(self, database):
        self._database = database

    def get_user(self, user_information: dict):
        assert "cpf" in user_information or "email" in user_information

        if "cpf" not in user_information:
            assert user_information["email"]

        try:
            query = User.select()

            if "cpf" in user_information:
                cpf = user_information["cpf"]
                query = query.where(User.cpf == cpf)

            if "email" in user_information:
                email = user_information["email"]
                if email is None:
                    query = query.where(User.email.is_null())
                else:
                    query = query.where(User.email == email)

            result = query.execute()

            assert len(result) == 1  #: This never may fail.
            return result[0]
        except User.DoesNotExist:
            return None

    def create_user(self, user_information: dict):
        assert "cpf" in user_information
        assert "password" in user_information
        assert "display_name" in user_information

        cpf = user_information["cpf"]
        password = user_information["password"]
        email = user_information.get("email")
        display_name = user_information["display_name"]

        if not is_valid_cpf(cpf):
            raise ValueError(f'String "{cpf}" is not a valid CPF')

        try:
            return (
                User.create(
                    cpf=cpf, password=password, display_name=display_name, email=email
                ),
                True,
            )
        except peewee.IntegrityError:
            return None, False

    def update_user_last_login(self, user_information: dict = None, user: User = None):
        assert user_information is not None or user is not None
        assert user_information is None or user is None

        now = datetime.datetime.utcnow()
        query = User.update(last_login=now)

        if user_information is not None:
            assert "cpf" in user_information or "email" in user_information

            if "cpf" not in user_information:
                assert user_information["email"]

            if "cpf" in user_information:
                cpf = user_information["cpf"]
                query = query.where(User.cpf == cpf)

            if "email" in user_information:
                email = user_information["email"]
                if email is None:
                    query = query.where(User.email.is_null())
                else:
                    query = query.where(User.email == email)

        elif user is not None:
            query = query.where(User == user)
        return query.execute() != 0

    def get_sessions(self, session_information: dict):
        assert "user" in session_information or "token" in session_information

        try:
            query = Session.select()

            if "user" in session_information:
                user = session_information["user"]
                query = query.where(Session.user == user)

            if "token" in session_information:
                token = session_information["token"]
                query = query.where(Session.token == token)

            return query.execute()
        except Session.DoesNotExist:
            return None

    def create_session(self, session_information: dict = None):
        assert "user" in session_information
        assert "token" in session_information

        try:
            user = session_information["user"]
            token = session_information["token"]
            return Session.create(user=user, token=token), True
        except peewee.IntegrityError:
            return None, False

    def expire_sessions(
        self, session_information: dict = None, session: Session = None
    ):
        assert session_information is not None or session is not None
        assert session_information is None or session is None

        now = datetime.datetime.utcnow()
        query = Session.update(expire_date=now)

        if session_information is not None:
            assert "user" in session_information or "token" in session_information

            if "user" in session_information:
                user = session_information["user"]
                query = query.where(Session.user == user)

            if "token" in session_information:
                token = session_information["token"]
                query = query.where(Session.token == token)

        elif session is not None:
            query = query.where(Session == session)

        return query.execute() != 0
