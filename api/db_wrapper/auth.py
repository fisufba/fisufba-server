import datetime
import secrets
from typing import Set, Tuple

import bcrypt
import peewee
from werkzeug.exceptions import BadRequest, Forbidden, Conflict, NotFound

import utils
from db.models import auth


class User:
    """Python class that abstracts or wraps the auth.User methods.

    Attributes:
        id: the User's id.
        cpf: the User's CPF.
        display_name: the User's display name.
        email: the User's email.

    """

    def __init__(self, cpf: str = None, password: str = None, _user: auth.User = None):
        """Initializes this User.

        Notes:
            It only accept two kinds of argument combination:
                0 - `cpf` is not None, `password` is not None and `_user` is None;
                1 - `cpf` is None, `password` is None and `_user` is not None.
            The latter combination is for internal purposes only.

        Args:
            cpf: the auth.User's CPF.
            password: the auth.User's password.
            _user: this User representation in the database.

        """
        if _user is None:
            assert cpf is not None
            assert password is not None

            if not utils.is_valid_cpf(cpf):
                raise BadRequest("Invalid cpf")

            try:
                _user = auth.User.get(cpf=utils.unmask_cpf(cpf))
            except auth.User.DoesNotExist:
                raise Forbidden("User does not exist")

            if not bcrypt.checkpw(
                password.encode("utf-8"), _user.password.encode("utf-8")
            ):
                raise Forbidden("Password is wrong")
        else:
            assert cpf is None
            assert password is None

        self._user = _user
        self.id = self._user.id
        self.cpf = utils.mask_cpf(self._user.cpf)
        self.display_name = self._user.display_name
        self.email = self._user.email

        self._group_names = set(
            group.name
            for group in auth.Group.select(auth.Group.name)
            .join(auth.UserGroups)
            .switch(auth.Group)
            .where(auth.UserGroups.user == self._user)
        )

        self._permissions = set(
            permission.codename
            for permission in auth.Permission.select(auth.Permission.codename)
            .join(auth.GroupPermissions)
            .join(auth.Group)
            .switch(auth.Permission)
            .where(auth.Group.name.in_(self._group_names))
        )

    def create_session(self) -> str:
        """Creates an auth.Session in the database.

        Returns:
            The token of the created auth.Session.

        """
        session, session_token = None, None
        while session_token is None:
            try:
                session = auth.Session.create(
                    user=self._user, token=secrets.token_hex(64)
                )
                session_token = session.token
            except peewee.IntegrityError:
                continue

        query = auth.User.update(last_login=datetime.datetime.utcnow()).where(
            auth.User.id == self.id
        )
        if query.execute() == 0:
            auth.Session.update(expire_date=datetime.datetime.utcnow()).where(
                auth.Session.token == session_token
            )
            # This is indeed an internal server error.
            raise Exception("Login Failed")

        return session_token

    def create_user(
        self,
        cpf: str,
        password: str,
        display_name: str,
        email: str,
        user_group_names: Set[str],
    ) -> int:
        """Creates an auth.User in the database.

        Args:
            cpf: the auth.User's CPF.
            password: the auth.User's password.
            display_name: the auth.User's display name.
            email: the auth.User's email.
            user_group_names: the group names to which the auth.User belongs.

        Returns:
            The id of the created auth.User.

        """
        if not utils.is_valid_cpf(cpf):
            raise BadRequest("Invalid cpf")
        if email is not None and not utils.is_valid_email(email):
            raise BadRequest("Invalid email")

        user_groups = auth.Group.select().where(auth.Group.name.in_(user_group_names))
        if len(user_groups) != len(user_group_names):
            raise BadRequest("Invalid group_names")

        required_permissions = set(
            f"create_{group_name}" for group_name in user_group_names
        )
        if len(required_permissions.difference(self._permissions)) > 0:
            raise Forbidden("Not enough permission")

        try:
            user = auth.User.create(
                cpf=utils.unmask_cpf(cpf),
                password=bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8"),
                display_name=display_name,
                email=email,
                is_verified=None if email is None else False,
            )
        except peewee.IntegrityError:
            raise Conflict("User already exists")

        try:
            for group in user_groups:
                auth.UserGroups.create(user=user, group=group)
        except peewee.IntegrityError:
            auth.User.delete().where(auth.User.id == user.id)
            raise Conflict("Duplicated user_group relation")

        return user.id

    def get_user(self, user_id: int) -> Tuple[auth.User, Set[str]]:
        """Retrieves an auth.User from the database.

        Args:
            user_id: the id of the target auth.User.

        Returns:
            An auth.User from the database.

        """
        user_group_names = set(
            group.name
            for group in auth.Group.select(auth.Group.name)
            .join(auth.UserGroups)
            .join(auth.User)
            .switch(auth.Group)
            .where(auth.User.id == user_id)
        )

        required_permissions = set(
            f"read_{group_name}_data" for group_name in user_group_names
        )
        if len(required_permissions.difference(self._permissions)) > 0:
            raise Forbidden("Not enough permission")

        try:
            return auth.User.get(id=user_id), user_group_names
        except auth.User.DoesNotExist:
            raise NotFound("User not found")

    def update_user(self, user_id: int, **kwargs):
        """Retrieves an auth.User from the database.

        Args:
            user_id: the id of the target auth.User.
            **kwargs: kwargs that may contain:
                cpf: the new auth.User's CPF.
                password: the new auth.User's password.
                display_name: the new auth.User's display name.
                email: the new auth.User's email.

        """
        user_group_names = set(
            group.name
            for group in auth.Group.select(auth.Group.name)
            .join(auth.UserGroups)
            .join(auth.User)
            .switch(auth.Group)
            .where(auth.User.id == user_id)
        )

        required_permissions = set(
            f"change_{group_name}_data" for group_name in user_group_names
        )
        if len(required_permissions.difference(self._permissions)) > 0:
            raise Forbidden("Forbidden")

        kwargs = dict(kwargs)
        valid_keys = {"cpf", "password", "display_name", "email"}
        for key in kwargs:
            assert key in valid_keys

        if "cpf" in kwargs:
            if not utils.is_valid_cpf(kwargs["cpf"]):
                raise BadRequest("Invalid cpf")
            kwargs["cpf"] = utils.unmask_cpf(kwargs["cpf"])

        if "password" in kwargs:
            kwargs["password"] = bcrypt.hashpw(
                kwargs["password"].encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

        if "email" in kwargs and kwargs["email"] is not None:
            if not utils.is_valid_email(kwargs["email"]):
                raise BadRequest("Invalid email")

        query = auth.User.update(**kwargs).where(auth.User.id == user_id)
        if query.execute() == 0:
            # Is this an internal server error?
            raise Exception("Not updated")


class Session:
    """Python class that abstracts or wraps the auth.Session methods.

    Attributes:
        token: the Session's token.
        user: the Session's User.

    """

    def __init__(self, token: str):
        """Initializes this Session.

        Args:
            token: the auth.Session's token.

        """
        try:
            self._session = auth.Session.get(token=token)
        except auth.Session.DoesNotExist:
            raise Forbidden("Invalid session token")

        if self._session.expire_date <= datetime.datetime.utcnow():
            #: Trying to authenticate an expired session.
            raise Forbidden("Expired token")

        self.token = self._session.token
        self.user = User(_user=self._session.user)

    def __eq__(self, other):
        if not isinstance(other, Session):
            return False
        return self.token == other.token and self.user.id == other.user.id

    def expire(self):
        """Updates the expire_date of this Session representation in the database for uctnow.

        """
        query = auth.Session.update(expire_date=datetime.datetime.utcnow()).where(
            auth.Session.id == self._session.id
        )
        if query.execute() == 0:
            raise Forbidden("Invalid session")