import datetime

import peewee

from db.models.auth import User, Session


class Auth:
    def __init__(self, database):
        self._database = database

    def get_user(self, *, cpf=None, email=None):
        if cpf is None and email is None:
            raise Exception

        try:
            if email is None:
                return User.get(cpf=cpf)
            elif cpf is None:
                return User.get(email=email)
            return User.get(cpf=cpf, email=email)
        except User.DoesNotExist:
            return None

    def create_user(self, cpf, password, display_name, email=None):

        # TODO cpf validation.

        try:
            return (
                User.create(
                    cpf=cpf, password=password, display_name=display_name, email=email
                ),
                True,
            )
        except peewee.IntegrityError:
            return None, False

    def create_session(self, user, token):

        try:
            return Session.create(user=user, token=token), True
        except peewee.IntegrityError:
            return None, False

    def expire_session(self, token):

        now = datetime.datetime.utcnow()
        query = Session.update(expire_date=now).where(
            (Session.token == token) & (Session.expire_date > now)
        )
        return query.execute() != 0
