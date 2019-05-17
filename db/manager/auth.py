import datetime

import peewee

from db.models.auth import User, Session
from utils.validation import is_valid_cpf, is_valid_email


class Auth:
    def __init__(self, database):
        self._database = database

    def get_user(self, user_information: dict = None, user_id: int = None):
        """Retrieves an User from the database.

        Args:
            user_information: dict that contains user's main information.
                It may contain the user's non-masked cpf and/or email.
                Other information won't be useful.
            user_id: the id of the target user. If None it won't be considered.

        Returns:
            An User from the database in case of its existence. None otherwise.

        """
        assert user_information is not None or user_id is not None

        if user_id is None:
            assert "cpf" in user_information or "email" in user_information

            #: Many users with cpf=None may exist. So it's not possible to retrieve them all.
            if "cpf" not in user_information:
                assert user_information["email"]

        try:
            query = User.select()

            if user_id is not None:
                query = query.where(User.id == user_id)

            if user_information is not None:
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

            assert len(result) == 1  #: This should never fail.
            return result[0]
        except User.DoesNotExist:
            return None

    def create_user(self, user_information: dict):
        """Creates an User in the database.

        Args:
            user_information: dict which contains all user's information.
                It must contain:
                    non-masked cpf;
                    password;
                    (optionally) email;
                    display_name.

        Returns:
            A tuple that contains:
                The created User and True if an user was created;
                None and False otherwise.

        """
        assert "cpf" in user_information
        assert "password" in user_information
        assert "display_name" in user_information

        cpf = user_information["cpf"]
        password = user_information["password"]
        display_name = user_information["display_name"]
        email = user_information.get("email")

        #: cpf validation.
        if not is_valid_cpf(cpf, with_mask=False):
            raise ValueError(f'"{cpf}" is not a valid non-masked CPF')

        #: email validation.
        if email is not None and is_valid_email(email):
            raise ValueError(f'"{email}" is not a valid email')

        #: other validation will occur by the database (e.g. password length).

        try:
            return (
                User.create(
                    cpf=cpf, password=password, display_name=display_name, email=email
                ),
                True,
            )
        except peewee.IntegrityError:
            return None, False

    def update_user_last_login(
        self, user_information: dict = None, user_id: int = None
    ):
        """Updates the last_login of a User in the database.

        Args:
            user_information: dict that contains user's main information.
                It may contain the user's non-masked cpf and/or email.
                Other information won't be useful.
            user_id: the id of the target user. If None it won't be considered.

        Returns:
            True when a User database row was updated. False otherwise.

        """
        assert user_information is not None or user_id is not None

        if user_id is None:
            assert "cpf" in user_information or "email" in user_information

            #: Many users with cpf=None may exist. So it's not possible to update them all.
            if "cpf" not in user_information:
                assert user_information["email"]

        now = datetime.datetime.utcnow()
        query = User.update(last_login=now)

        if user_id is not None:
            query = query.where(User.id == user_id)

        if user_information is not None:
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
        assert result <= 1  #: This should never fail.
        return result != 0

    def get_sessions(self, session_information: dict):
        """Retrieves Sessions from the database.

        Args:
            session_information: dict that contains sessions' main information.
                It may contain the sessions' respective user or token.
                Other information won't be useful.

        Returns:
            List of all Session found in the database using `session_information`
                or None it no Session was found.

        """
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

    def create_session(self, session_information: dict):
        """Creates an User in the database.

        Args:
            session_information: dict that contains session's information.
                It must contain the session's respective user and token.

        Returns:
            A tuple that contains:
                The created Session and True if an user was created;
                None and False otherwise.

        """
        assert "user" in session_information
        assert "token" in session_information

        try:
            user = session_information["user"]
            token = session_information["token"]
            return Session.create(user=user, token=token), True
        except peewee.IntegrityError:
            return None, False

    def expire_sessions(self, session_information: dict = None, session_id: int = None):
        """Updates the expire_date of Sessions in the database for uctnow.

        Args:
            session_information: dict that contains session's information.
                It must contain the session's respective user or token.
            session_id: the id of a target session. If None it won't be considered.

        Returns:
            True when any Session database row was updated. False otherwise.

        """
        assert session_information is not None or session_id is not None

        if session_id is None:
            assert "user" in session_information or "token" in session_information

        now = datetime.datetime.utcnow()
        query = Session.update(expire_date=now)

        if session_id is not None:
            query = query.where(Session.id == session_id)

        if session_information is not None:
            if "user" in session_information:
                user = session_information["user"]
                query = query.where(Session.user == user)

            if "token" in session_information:
                token = session_information["token"]
                query = query.where(Session.token == token)

        return query.execute() != 0
