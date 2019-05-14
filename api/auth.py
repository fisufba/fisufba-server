import secrets

import bcrypt
from flask import request, url_for

from utils.api import AppResource
from utils.utils import is_valid_cpf, is_valid_email
from db.manager import manager as dbman


class _Signup(AppResource):

    """AppResource responsible for the logup and logoff processes an Api.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Returns:
            An url path.

        """
        return "/accounts/signup"

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

    def post(self):

        """Treats HTTP POST requests.

        If there's no running session and valid credentials are posted
        it performs an user login.

        Notes:
            For better understanding, refer: http://stateless.co/hal_specification.html.

        Raises:
            TODO.

        Returns:
            Dict object following the HAL format.

        """

        #  TODO check if the user has privileges to create another user

        cpf = request.form.get("cpf")
        password = request.form.get("password")
        display_name = request.form.get("display_name")
        email = request.form.get("email")

        # checking whether the variables are strings
        if not isinstance(cpf, str):
            raise Exception("Invalid cpf")
        if not isinstance(password, str):
            raise Exception("Invalid password")
        if not isinstance(display_name, str):
            raise Exception("Invalid display_name")

        if not is_valid_cpf(cpf):
            raise Exception("Invalid cpf")  # TODO InvalidCPFError.

        if not email is None and not is_valid_email(email):
            raise Exception("Invalid email")  # TODO InvalidEmailError.

        user, created = dbman.auth.create_user(
            user_information={
                "cpf": cpf,
                "password": bcrypt.hashpw(
                    password.encode("utf-8"), bcrypt.gensalt()
                ).decode("utf-8"),
                "display_name": display_name,
                "email": email,
            }
        )

        if not created:
            raise Exception("User wasn't stored")  # TODO User not created

        return {"_links": {"self": {"href": self.get_path()}}, "created": created}


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

        if request.form.get("Authentication") is not None:
            raise Exception("Logout required")  # TODO AuthenticatedError.

        cpf = request.form.get("cpf")
        password = request.form.get("password")

        if not isinstance(cpf, str):
            raise Exception("Invalid cpf")  # TODO InvalidCPFError.
        if not isinstance(password, str):
            raise Exception("Invalid password")  # TODO InvalidPasswordError.

        if not is_valid_cpf(cpf):
            raise Exception("Invalid cpf")  # TODO InvalidCPFError.
        target_user = dbman.auth.get_user({"cpf": cpf})
        if target_user is None:
            raise Exception("Invalid cpf")  # TODO InvalidCPFError.

        if not bcrypt.checkpw(
            password.encode("utf-8"), target_user.password.encode("utf-8")
        ):
            raise Exception("Invalid password")  # TODO InvalidPasswordError.
        # TODO check password's min and max length.

        session, session_token = None, None
        while session_token is None:
            session, created = dbman.auth.create_session(
                {"user": target_user, "token": secrets.token_hex(64)}
            )
            if created:
                session_token = session.token

        #: True if the login was successful, False otherwise.
        logged_in = dbman.auth.update_user_last_login(user=target_user)

        if not logged_in:
            dbman.auth.expire_sessions(session=session)
            session_token = None

        return {
            "_links": {"self": {"href": self.get_path()}},
            "logged_in": logged_in,
            "token": session_token,
        }


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
        session_token = request.form.get("Authentication")

        if session_token is None:
            raise Exception("Login required")  # TODO UnauthenticatedError.
        if not isinstance(session_token, str):
            raise Exception("Invalid session token")  # TODO InvalidSessionTokenError.
        if len(session_token) != 128:
            raise Exception("Invalid session token")  # TODO InvalidSessionTokenError.

        target_session = dbman.auth.get_sessions({"token": session_token})[0]

        if target_session is None:
            raise Exception("Invalid session token")  # TODO InvalidSessionTokenError.

        #: True if the logout was successful, False otherwise.
        logged_out = dbman.auth.expire_sessions(session=target_session)

        return {
            "_links": {
                "self": {"href": self.get_path()},
                "curies": [{"name": "rd", "href": "TODO/{rel}", "templated": True}],
                "rd:index": {"href": url_for("_index"), "templated": True},
            },
            "logged_out": logged_out,
        }
