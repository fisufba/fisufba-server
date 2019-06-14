from flask import g, request, url_for
from werkzeug.exceptions import BadRequest, Forbidden

from api.abc import AppResource
from api.abc import authentication_required, unauthentication_required
from api.db_wrapper.auth import User, Session
from api.search import search_user


class _Signup(AppResource):
    """AppResource responsible for User account creation.

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
        post_body = request.get_json()

        try:
            cpf = post_body["cpf"]
        except KeyError:
            raise BadRequest("cpf field is missing")

        try:
            password = post_body["password"]
        except KeyError:
            raise BadRequest("password field is missing")

        try:
            display_name = post_body["display_name"]
        except KeyError:
            raise BadRequest("display_name field is missing")

        try:
            phone = post_body["phone"]
        except KeyError:
            raise BadRequest("phone field is missing")

        try:
            email = post_body["email"]
        except KeyError:
            raise BadRequest("email field is missing")

        try:
            user_group_names = post_body["user_group_names"]
        except KeyError:
            raise BadRequest("user_group_names field is missing")

        # checking whether the variables are strings
        if not isinstance(cpf, str):
            raise BadRequest("cpf is not a string")
        if not isinstance(password, str):
            raise BadRequest("password is not a string")
        if not isinstance(display_name, str):
            raise BadRequest("display_name is not a string")
        if phone is not None and not isinstance(phone, str):
            raise BadRequest("phone is not a string")
        if email is not None and not isinstance(email, str):
            raise BadRequest("email is not a string")
        if not isinstance(user_group_names, list):
            raise BadRequest("user_group_names is not a list")

        if len(user_group_names) != len(set(user_group_names)):
            raise BadRequest("user_group_names contains duplicate names")

        user_id = g.session.user.create_user(
            cpf=cpf,
            password=password,
            display_name=display_name,
            phone=phone,
            email=email,
            user_group_names=set(user_group_names),
        )

        return {"_links": {"self": {"href": url_for("_signup")}}, "user_id": user_id}


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
        post_body = request.get_json()

        try:
            cpf = post_body["cpf"]
        except KeyError:
            raise BadRequest("cpf field is missing")

        try:
            password = post_body["password"]
        except KeyError:
            raise BadRequest("password field is missing")

        if not isinstance(cpf, str):
            raise BadRequest("cpf is not a string")
        if not isinstance(password, str):
            raise BadRequest("password is not a string")

        target_user = User(cpf, password)
        session_token = target_user.create_session()

        return {
            "_links": {"self": {"href": url_for("_login")}},
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
        post_body = request.get_json()

        try:
            session_token = post_body["token"]
        except KeyError:
            raise BadRequest("token field is missing")

        if not isinstance(session_token, str):
            raise BadRequest("token is not a string")

        target_session = Session(session_token)
        if target_session != g.session:
            raise Forbidden("trying to logout of another session")

        target_session.expire()

        return {
            "_links": {"self": {"href": url_for("_logout")}},
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
        return "/accounts/<int:user_id>"

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
    def get(self, user_id: int):
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
        return {
            "_links": {"self": {"href": url_for("_account", user_id=user_id)}},
            "user": g.session.user.get_serialized_user(user_id),
        }

    @authentication_required
    def patch(self, user_id: int):
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
        patch_body = request.get_json()

        kwargs = {}

        if "cpf" in patch_body:
            cpf = patch_body["cpf"]
            if not isinstance(cpf, str):
                raise BadRequest("cpf is not a string")
            kwargs["cpf"] = cpf

        if "password" in patch_body:
            password = patch_body["password"]
            if not isinstance(password, str):
                raise BadRequest("password is not a string")
            kwargs["password"] = password

        if "display_name" in patch_body:
            display_name = patch_body["display_name"]
            if not isinstance(display_name, str):
                raise BadRequest("display_name is not a string")
            kwargs["display_name"] = display_name

        if "phone" in patch_body:
            phone = patch_body["phone"]
            if phone is not None and not isinstance(phone, str):
                raise BadRequest("phone is not a string")
            kwargs["phone"] = phone

        if "email" in patch_body:
            email = patch_body["email"]
            if email is not None and not isinstance(email, str):
                raise BadRequest("email is not a string")
            kwargs["email"] = email

        g.session.user.update_user(user_id, **kwargs)

        return {
            "_links": {"self": {"href": url_for("_account", user_id=user_id)}},
            "user_id": user_id,
        }


class _Search(AppResource):
    """AppResource responsible for search an user.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Returns:
            An url path.

        """
        return "/accounts/search"

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

    @classmethod
    @authentication_required
    def get(self):

        kwargs = {}

        cpf = request.args.get("cpf", None)

        display_name = request.args.get("display_name", None)

        phone = request.args.get("phone", None)

        email = request.args.get("email", None)

        if cpf is not None:
            if not isinstance(cpf, str):
                raise BadRequest("cpf is not a string")
            kwargs["cpf"] = cpf

        if display_name is not None:
            if not isinstance(display_name, str):
                raise BadRequest("display_name is not a string")
            kwargs["display_name"] = display_name

        if phone is not None:
            if not isinstance(phone, str):
                raise BadRequest("phone is not a string")
            kwargs["phone"] = phone

        if email is not None:
            if not isinstance(email, str):
                raise BadRequest("email is not a string")
            kwargs["email"] = email

        query = search_user(**kwargs)

        return {
            "_links": {"self": {"href": url_for("_search")}},
            "_embedded": {
                "items": [
                    {
                        "type": "user",
                        "_embedded": g.session.user.get_serialized_user(user.id),
                    }
                    for user in query
                ]
            },
        }


def authentication():
    if hasattr(g, "session"):
        # This is indeed an internal server error.
        raise Exception("inconsistent value found")

    session_token = request.headers.get("Authorization")
    if session_token is None:
        g.session = None
    else:
        if not isinstance(session_token, str):
            raise BadRequest("invalid session token")
        if not session_token.startswith("fisufba "):
            raise BadRequest("invalid session token")
        g.session = Session(session_token[8:])


def unauthentication(response):
    if hasattr(g, "session"):
        g.pop("session")
    return response


BEFORE_REQUEST_FUNCS = (authentication,)
AFTER_REQUEST_FUNCS = (unauthentication,)
