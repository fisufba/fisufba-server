import inspect
from importlib import import_module
from types import FunctionType
from typing import Set, Type

from flask import Flask
from flask_restful import Api

from api.abc import AppResource


def get_app_resources(module_name: str) -> Set[Type[AppResource]]:
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


def get_before_request_funcs(module_name: str) -> Set[FunctionType]:
    """Retrieves a set of functions from `BEFORE_REQUEST_FUNCS`
        attribute from a Module.

    Args:
        module_name: The name of the target Module.

    Raises:
        AssertionError: When the `BEFORE_REQUEST_FUNCS` attribute
            includes something that is not a function.

    Returns:
        Functions included in the `BEFORE_REQUEST_FUNCS` attribute
            of the target Module which name is `module_name`.

    """
    module = import_module(module_name)

    if not hasattr(module, "BEFORE_REQUEST_FUNCS"):
        return set()
    funcs = getattr(module, "BEFORE_REQUEST_FUNCS")
    for func in funcs:
        assert isinstance(func, FunctionType)
    return set(funcs)


def get_after_request_funcs(module_name: str) -> Set[FunctionType]:
    """Retrieves a set of functions from `AFTER_REQUEST_FUNCS`
        attribute from a Module.

    Args:
        module_name: The name of the target Module.

    Raises:
        AssertionError: When the `AFTER_REQUEST_FUNCS` attribute
            includes something that is not a function.

    Returns:
        Functions included in the `AFTER_REQUEST_FUNCS` attribute
            of the target Module which name is `module_name`.

    """
    module = import_module(module_name)

    if not hasattr(module, "AFTER_REQUEST_FUNCS"):
        return set()
    funcs = getattr(module, "AFTER_REQUEST_FUNCS")
    for func in funcs:
        assert isinstance(func, FunctionType)
    return set(funcs)


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


def add_before_request_funcs(app: Flask, funcs: Set[FunctionType]):
    """Adds a set of functions into an Flask application
        to be called before each request.

    Args:
        app: Instance of the target Flask application.
        funcs: Set of functions to be added.

    Raises:
        AssertionError: When it tries to add an function that
            was previously added in `app`.

    """
    for func in funcs:
        assert func not in app.before_request_funcs.get(None, [])
        app.before_request(func)


def add_after_request_funcs(app: Flask, funcs: Set[FunctionType]):
    """Adds a set of functions into an Flask application
        to be called after each request.

    Args:
        app: Instance of the target Flask application.
        funcs: Set of functions to be added.

    Raises:
        AssertionError: When it tries to add an function that
            was previously added in `app`.

    """
    for func in funcs:
        assert func not in app.after_request_funcs.get(None, [])
        app.after_request(func)


def add_resources_from(api: Api, module_name: str):
    """Adds a set of AppResource classes from a Module into an Api
        and also adds a set of functions included in the `BEFORE_REQUEST_FUNCS`
        and `AFTER_REQUEST_FUNCS` attribute of the Module
        into the Api's Flask application.

    It also do the same for each dependencies defined in a treated AppResource.

    Args:
        api: Instance of the target Api.
        module_name: The name of the target Module.

    Raises:
        AssertionError: When there's a dependency cycle.

    """
    app_resources = get_app_resources(module_name)
    before_request_funcs = get_before_request_funcs(module_name)
    after_request_funcs = get_after_request_funcs(module_name)

    add_app_resources(api, app_resources)
    add_before_request_funcs(api.app, before_request_funcs)
    add_after_request_funcs(api.app, after_request_funcs)

    dep_names = set()
    for app_res in app_resources:
        dep_names.update(app_res.get_dependencies())

    seen_module_names = {module_name}
    while len(dep_names) > 0:
        dep_name = dep_names.pop()

        assert dep_name not in seen_module_names

        app_resources = get_app_resources(dep_name)
        before_request_funcs = get_before_request_funcs(dep_name)
        after_request_funcs = get_after_request_funcs(dep_name)

        add_app_resources(api, app_resources)
        add_before_request_funcs(api.app, before_request_funcs)
        add_after_request_funcs(api.app, after_request_funcs)

        for app_res in app_resources:
            app_res_dep_names = app_res.get_dependencies()
            app_res_dep_names.difference_update(seen_module_names)

            dep_names.update(app_res_dep_names)

        seen_module_names.add(dep_name)
