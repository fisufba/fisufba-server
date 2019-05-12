import inspect
from abc import abstractmethod
from importlib import import_module
from typing import Set, Type

from flask_restful import Api, Resource


class AppResource(Resource):
    """Defines the class of an application resource.

    """

    @classmethod
    @abstractmethod
    def get_path(cls) -> str:
        """Returns the url path of this AppResource.

        Raises:
            NotImplementedError: When not implemented by AppResource's children.

        Returns:
            An url path.

        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_dependencies(cls) -> Set[str]:
        """Returns the dependencies of this AppResource.

        Notes:
            If there's no dependency this must return an empty set.

        Raises:
            NotImplementedError: When not implemented by AppResource's children.

        Returns:
            A set of module names that contains AppResource
                classes used by this AppResource.

        """
        raise NotImplementedError


def get_app_resources(module_name) -> Set[Type[AppResource]]:
    """Retrieves AppResource classes from a Module.

    Args:
        module_name: The name of the target Module.

    Returns:
        AppResource classes defined in the Module
            which name is `module_name`.

    """
    module = import_module(module_name)

    app_resources = set()
    for _, cls in inspect.getmembers(module, inspect.isclass):
        if inspect.getmodule(cls) is not module:
            continue
        if not issubclass(cls, AppResource):
            continue
        app_resources.add(cls)
    return app_resources


def add_app_resources(api: Api, app_resources: Set[Type[AppResource]]):
    """Adds a set of AppResource classes into an Api.

    Args:
        api: Instance of the target Api.
        app_resources: Set of AppResource classes to be added.

    Raises:
        AssertionError: When it tries to add an AppResource that
            was previously added in `api`.
        AssertionError: When it tries to add an AppResource with
            a path that already exists in `api`.

    """
    for app_res in app_resources:
        assert app_res not in api.resources
        assert app_res.get_path() not in api.urls
        api.add_resource(app_res, app_res.get_path())


def add_app_resources_from(api: Api, module_name: str):
    """Adds a set of AppResource classes from a Module into an Api.

    It also adds all dependencies of all added AppResource classes.

    Args:
        api: Instance of the target Api.
        module_name: The name of the target Module.

    Raises:
        AssertionError: When there's a dependency cycle.

    """
    app_resources = get_app_resources(module_name)

    add_app_resources(api, app_resources)

    dep_names = set()
    for app_res in app_resources:
        dep_names.update(app_res.get_dependencies())

    seen_module_names = {module_name}
    while len(dep_names) > 0:
        dep_name = dep_names.pop()

        assert dep_name not in seen_module_names

        app_resources = get_app_resources(dep_name)

        add_app_resources(api, app_resources)

        for app_res in app_resources:
            app_res_dep_names = app_res.get_dependencies()
            app_res_dep_names.difference_update(seen_module_names)

            dep_names.update(app_res_dep_names)

        seen_module_names.add(dep_name)
