from utils.api import AppResource
from api.auth import _Accounts, _LogIn, _LogOut


class _Index(AppResource):
    @classmethod
    def get_path(cls):
        return "/"

    @classmethod
    def get_dependencies(cls):
        return {"api.auth"}

    def get(self):
        return {
            "_links": {
                "self": {"href": self.get_path()},
                "curies": [{"name": "auth", "href": "TODO/{rel}", "templated": True}],
                "auth:accounts": {"href": _Accounts.get_path(), "templated": True},
                "auth:login": {"href": _LogIn.get_path(), "templated": True},
                "auth:logout": {"href": _LogOut.get_path(), "templated": True},
            }
        }
