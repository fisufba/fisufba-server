from flask import url_for

from api.abc import AppResource


class _Index(AppResource):
    """AppResource responsible for an Api index.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Returns:
            An url path.

        """
        return "/"

    @classmethod
    def get_dependencies(cls):
        """Returns the dependencies of this AppResource.

        Notes:
            If there's no dependency this must return an empty set.

        Returns:
            A set of module names that contains AppResource
                classes used by this AppResource.

        """
        return {"api.auth", "api.forms"}

    def get(self):
        """Treats HTTP GET requests.

        It shows the possible paths to follow.

        Notes:
            For better understanding, refer: http://stateless.co/hal_specification.html.

        Returns:
            Dict object following the HAL format.

        """
        return {
            "_links": {
                "self": {"href": url_for("_index")},
                "curies": [
                    {"name": "auth", "href": "TODO/{rel}", "templated": True},
                    {"name": "forms", "href": "TODO/{rel}", "templated": True},
                ],
                "auth:signup": {"href": url_for("_signup"), "templated": True},
                "auth:login": {"href": url_for("_login"), "templated": True},
                "auth:logout": {"href": url_for("_logout"), "templated": True},
                "auth:account": {
                    "href": url_for("_account", user_id=0),
                    "templated": True,
                },
                "forms:index": {"href": url_for("formsindex"), "templated": True},
            }
        }
