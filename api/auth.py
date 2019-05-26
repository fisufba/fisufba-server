import secrets
import datetime

import bcrypt
from flask import g, request, url_for

from api.abc import AppResource
from api.abc import authentication_required, unauthentication_required
from db.manager import manager as dbman
from utils.validation import is_valid_cpf, is_valid_email


class _Signup(AppResource):
    """AppResource responsible for User account creation and deletion.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Returns:
            An url path.

        """
        return "/accounts"

    @classmethod
    def get_dependencies(cls):
        """Returns the dependencies of this AppResource.

        Notes:
            If there's no dependency this must return an empty set.

        Returns:
            A set of module names that contains AppResource
                classes used by this AppResource.

        """
        return set()

    @authentication_required
    def post(self):
        """Treats HTTP POST requests.

        If there's a running session and valid credentials are posted
        it performs may an new_user creation if the current new_user has the
        appropriate permissions.

        Notes:
            For better understanding, refer: http://stateless.co/hal_specification.html.

        Raises:
            TODO.

        Returns:
            Dict object following the HAL format
                with information about the execution.

        """
        cpf = request.form.get("cpf")
        password = request.form.get("password")
        display_name = request.form.get("display_name")
        email = request.form.get("email")
        group_name = request.form.get("group")

        # checking whether the variables are strings
        if not isinstance(cpf, str):
            raise Exception("Invalid cpf")  # TODO InvalidCPFError.
        if not isinstance(password, str):
            raise Exception("Invalid password")  # TODO InvalidPasswordError.
        if not isinstance(display_name, str):
            raise Exception("Invalid display_name")  # TODO InvaliDisplayNameError.
        if email is not None and not isinstance(email, str):
            raise Exception("Invalid email")  # TODO InvalidEmailError.
        if not isinstance(group_name, str):
            raise Exception("Invalid group_name")  # TODO InvalidGroupNameError.

        if not is_valid_cpf(cpf):
            raise Exception("Invalid cpf")  # TODO InvalidCPFError.

        if email is not None and not is_valid_email(email):
            raise Exception("Invalid email")  # TODO InvalidEmailError.

        if not dbman.auth.check_user_permission(
            getattr(g, "session").user, f"create_{group_name}"
        ):
            raise Exception("Forbidden")  # TODO ForbiddenError.

        new_user, created = dbman.auth.create_user(
            user_information={
                "cpf": cpf.replace(".", "").replace("-", ""),
                "password": bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8"),
                "display_name": display_name,
                "email": email,
                "group_name": group_name,
            }
        )

        if not created:
            raise Exception("User wasn't stored")  # TODO NotCreatedError.

        hal = {"_links": {"self": {"href": self.get_path()}}, "created": created}
        if created:
            hal["user_id"] = new_user.id
        return hal


class _Login(AppResource):
    """AppResource responsible for the login process of an Api.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Returns:
            An url path.

        """
        return "/accounts/login"

    @classmethod
    def get_dependencies(cls):
        """Returns the dependencies of this AppResource.

        Notes:
            If there's no dependency this must return an empty set.

        Returns:
            A set of module names that contains AppResource
                classes used by this AppResource.

        """
        return set()

    @unauthentication_required
    def post(self):
        """Treats HTTP POST requests.

        If there's no running session and valid credentials are posted
        it performs an user login.

        Notes:
            For better understanding, refer: http://stateless.co/hal_specification.html.

        Raises:
            TODO.

        Returns:
            Dict object following the HAL format
                with a session token (that may be valid or None).

        """
        cpf = request.form.get("cpf")
        password = request.form.get("password")

        if not isinstance(cpf, str):
            raise Exception("Invalid cpf")  # TODO InvalidCPFError.
        if not isinstance(password, str):
            raise Exception("Invalid password")  # TODO InvalidPasswordError.

        if not is_valid_cpf(cpf):
            raise Exception("Invalid cpf")  # TODO InvalidCPFError.

        target_user = dbman.auth.get_user(
            {"cpf": cpf.replace(".", "").replace("-", "")}
        )
        if target_user is None:
            raise Exception("Invalid cpf")  # TODO InvalidCPFError.

        if not bcrypt.checkpw(
            password.encode("utf-8"), target_user.password.encode("utf-8")
        ):
            raise Exception("Invalid password")  # TODO InvalidPasswordError.

        session, session_token = None, None
        while session_token is None:
            session, created = dbman.auth.create_session(
                {"user": target_user, "token": secrets.token_hex(64)}
            )
            if created:
                session_token = session.token

        #: True if the login was successful, False otherwise.
        logged_in = dbman.auth.update_user_last_login(user_id=target_user.id)

        if not logged_in:
            dbman.auth.expire_sessions(session_id=session.id)

        hal = {"_links": {"self": {"href": self.get_path()}}, "logged_in": logged_in}
        if logged_in:
            hal["user_id"] = target_user.id
            hal["token"] = session_token
        return hal


class _Logout(AppResource):
    """AppResource responsible for the logout process of an Api.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Returns:
            An url path.

        """
        return "/accounts/logout"

    @classmethod
    def get_dependencies(cls):
        """Returns the dependencies of this AppResource.

        Notes:
            If there's no dependency this must return an empty set.

        Returns:
            A set of module names that contains AppResource
                classes used by this AppResource.

        """
        return set()

    @authentication_required
    def post(self):
        """Treats HTTP POST requests.

        If there's a valid running session it performs the session logout.

        Notes:
            For better understanding, refer: http://stateless.co/hal_specification.html.

        Raises:
            TODO.

        Returns:
            Dict object following the HAL format
                with information about the execution.

        """

        session_token = request.form.get("token")

        if session_token is None:
            raise Exception("Session token not found")  # TODO BadRequestError.
        if not isinstance(session_token, str):
            raise Exception("Invalid session token")  # TODO InvalidSessionTokenError.
        if len(session_token) != 128:
            raise Exception("Invalid session token")  # TODO InvalidSessionTokenError.

        target_session = dbman.auth.get_session(session_token)
        if target_session is None:
            raise Exception("Invalid session token")  # TODO InvalidSessionTokenError.
        if target_session != getattr(g, "session"):
            #: Trying to logout a different session.
            raise Exception("Invalid session token")  # TODO InvalidSessionTokenError.
        if target_session.expire_date <= datetime.datetime.utcnow():
            #: Trying to logout an expired session.
            raise Exception("Invalid session")  # TODO InvalidSessionError.

        #: True if the logout was successful, False otherwise.
        logged_out = dbman.auth.expire_sessions(session_id=target_session.id)

        hal = {
            "_links": {
                "self": {"href": self.get_path()},
                "curies": [{"name": "rd", "href": "TODO/{rel}", "templated": True}],
                "rd:index": {"href": url_for("_index"), "templated": True},
            },
            "logged_out": logged_out,
        }
        if logged_out:
            hal["user_id"] = target_session.user.id
        return hal


class _Account(AppResource):
    """AppResource responsible for read and update user information.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Returns:
            An url path.

        """
        return "/account/<int:user_id>"

    @classmethod
    def get_dependencies(cls):
        """Returns the dependencies of this AppResource.

        Notes:
            If there's no dependency this must return an empty set.

        Returns:
            A set of module names that contains AppResource
                classes used by this AppResource.

        """
        return set()

    @authentication_required
    def get(self, user_id):
        """Treats HTTP GET requests.

        If there's a valid running session it returns the data of some User.

        Notes:
            For better understanding, refer: http://stateless.co/hal_specification.html.

        Args:
            user_id: The target id of the User.

        Raises:
            TODO.

        Returns:
            Dict object following the HAL format
                with information about the execution.

        """
        for group in dbman.auth.get_user_groups(user_id):
            if not dbman.auth.check_user_permission(
                getattr(g, "session").user, f"read_{group.name}_data"
            ):
                raise Exception("Forbidden")  # TODO ForbiddenError.

        user = dbman.auth.get_user(user_id=user_id)

        found = user is not None

        hal = {"_links": {"self": {"href": self.get_path()}}, "found": found}
        if found:
            hal["user"] = dict(
                id=user.id,
                cpf=user.cpf,
                display_name=user.display_name,
                email=user.email,
                is_active=user.is_active,
                is_verified=user.is_verified,
                last_login=user.last_login,
            )
        return hal

    @authentication_required
    def patch(self, user_id):
        """Treats HTTP GET requests.

        If there's a valid running session it performs a partial update in the
        data of the User that has id equals `user_id`.

        Notes:
            For better understanding, refer: http://stateless.co/hal_specification.html.

        Args:
            user_id: The target id of the User.

        Raises:
            TODO.

        Returns:
            Dict object following the HAL format
                with information about the execution.

        """
        for group in dbman.auth.get_user_groups(user_id):
            if not dbman.auth.check_user_permission(
                getattr(g, "session").user, f"read_{group.name}_data"
            ):
                raise Exception("Forbidden")  # TODO ForbiddenError.

        user_information = {}
        if "cpf" in request.form:
            cpf = request.form.get("cpf")
            if cpf is not None and not isinstance(cpf, str):
                raise Exception("Invalid cpf")  # TODO InvalidCPFError.
            if not is_valid_cpf(cpf):
                raise Exception("Invalid cpf")  # TODO InvalidCPFError.
            user_information["cpf"] = cpf

        if "password" in request.form:
            password = request.form.get("password")
            if password is not None and not isinstance(password, str):
                raise Exception("Invalid password")  # TODO InvalidPasswordError.
            user_information["password"] = password

        if "display_name" in request.form:
            display_name = request.form.get("display_name")
            if display_name is not None and not isinstance(display_name, str):
                raise Exception("Invalid display_name")  # TODO InvaliDisplayNameError.
            user_information["display_name"] = display_name

        if "email" in request.form:
            email = request.form.get("email")
            if email is not None and not isinstance(email, str):
                raise Exception("Invalid email")  # TODO InvalidEmailError.
            if email is not None and not is_valid_email(email):
                raise Exception("Invalid email")  # TODO InvalidEmailError.
            user_information["email"] = email

        updated = dbman.auth.update_user_information(
            user_information=user_information, user_id=user_id
        )

        hal = {"_links": {"self": {"href": self.get_path()}}, "updated": updated}
        if updated:
            hal["user_id"] = user_id
        return hal


def authentication():
    if hasattr(g, "session"):
        raise Exception("Inconsistent value found")

    session_token = request.headers.get("Authentication")
    if session_token is None:
        setattr(g, "session", None)
    else:
        if not isinstance(session_token, str):
            raise Exception("Invalid session token")  # TODO InvalidSessionTokenError.
        if len(session_token) != 128:
            raise Exception("Invalid session token")  # TODO InvalidSessionTokenError.

        session = dbman.auth.get_session(session_token)
        if session is None:
            raise Exception("Invalid session token")  # TODO InvalidSessionTokenError.
        if session.expire_date <= datetime.datetime.utcnow():
            #: Trying to logout an expired session.
            raise Exception("Invalid session")  # TODO InvalidSessionError.

        setattr(g, "session", session)


def unauthentication():
    if not hasattr(g, "session"):
        raise Exception("Inconsistent value found")

    g.pop("session")


BEFORE_REQUEST_FUNCS = (authentication,)
AFTER_REQUEST_FUNCS = (unauthentication,)
