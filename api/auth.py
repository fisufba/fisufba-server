from flask import g, request, url_for

import utils
from api.abc import AppResource
from api.abc import authentication_required, unauthentication_required
from db.wrapper.auth import User, Session


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
        group_names = request.form.get("group")

        # checking whether the variables are strings
        if not isinstance(cpf, str):
            raise Exception("Invalid cpf")  # TODO InvalidCPFError.
        if not isinstance(password, str):
            raise Exception("Invalid password")  # TODO InvalidPasswordError.
        if not isinstance(display_name, str):
            raise Exception("Invalid display_name")  # TODO InvaliDisplayNameError.
        if email is not None and not isinstance(email, str):
            raise Exception("Invalid email")  # TODO InvalidEmailError.

        if not isinstance(group_names, list):
            raise Exception("Invalid group_names")  # TODO InvalidGroupNamesError.
        if len(group_names) != len(set(group_names)):
            raise Exception("Duplicated group_name")  # TODO DuplicatedGroupNameError.
        for group_name in group_names:
            if not isinstance(group_name, str):
                raise Exception("Invalid group_name")  # TODO InvalidGroupNameError.

        user_id = getattr(g, "session").user.create_user(
            cpf=cpf,
            password=password,
            display_name=display_name,
            email=email,
            group_names=set(group_names),
        )

        return {"_links": {"self": {"href": self.get_path()}}, "user_id": user_id}


class _Login(AppResource):
    """AppResource responsible for the create_session process of an Api.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Returns:
            An url path.

        """
        return "/accounts/create_session"

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
        it performs an user create_session.

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

        target_user = User(cpf, password)
        session_token = target_user.create_session()

        return {
            "_links": {"self": {"href": self.get_path()}},
            "token": session_token,
            "user_id": target_user.id,
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

        target_session = Session(session_token)
        if target_session != getattr(g, "session"):
            #: Trying to logout a different session.
            raise Exception("Invalid session")  # TODO InvalidSessionError.

        target_session.expire()

        return {
            "_links": {
                "self": {"href": self.get_path()},
                "curies": [{"name": "rd", "href": "TODO/{rel}", "templated": True}],
                "rd:index": {"href": url_for("_index"), "templated": True},
            },
            "user_id": target_session.user.id,
        }


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

        user, user_group_names = getattr(g, "session").user.get_user(user_id)

        return {
            "_links": {"self": {"href": self.get_path()}},
            "user": dict(
                id=user.id,
                cpf=utils.mask_cpf(user.cpf),
                display_name=user.display_name,
                email=user.email,
                is_active=user.is_active,
                is_verified=user.is_verified,
                last_login=user.last_login,
                groups=list(user_group_names),
            ),
        }

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
        kwargs = {}
        if "cpf" in request.form:
            cpf = request.form["cpf"]
            if not isinstance(cpf, str):
                raise Exception("Invalid cpf")  # TODO InvalidCPFError.
            kwargs["cpf"] = cpf

        if "password" in request.form:
            password = request.form["password"]
            if not isinstance(password, str):
                raise Exception("Invalid password")  # TODO InvalidPasswordError.
            kwargs["password"] = password

        if "display_name" in request.form:
            display_name = request.form["display_name"]
            if not isinstance(display_name, str):
                raise Exception("Invalid display_name")  # TODO InvaliDisplayNameError.
            kwargs["display_name"] = display_name

        if "email" in request.form:
            email = request.form["email"]
            if email is not None and not isinstance(email, str):
                raise Exception("Invalid email")  # TODO InvalidEmailError.
            kwargs["email"] = email

        getattr(g, "session").user.update_user(user_id, **kwargs)

        return {"_links": {"self": {"href": self.get_path()}}, "user_id": user_id}


def authentication():
    if hasattr(g, "session"):
        raise Exception("Inconsistent value found")

    session_token = request.headers.get("Authentication")
    if session_token is None:
        setattr(g, "session", None)
    else:
        if not isinstance(session_token, str):
            raise Exception("Invalid session token")  # TODO InvalidSessionTokenError.
        setattr(g, "session", Session(session_token))


def unauthentication():
    if not hasattr(g, "session"):
        raise Exception("Inconsistent value found")
    g.pop("session")


BEFORE_REQUEST_FUNCS = (authentication,)
AFTER_REQUEST_FUNCS = (unauthentication,)
