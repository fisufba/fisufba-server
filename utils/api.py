import inspect
from abc import abstractmethod
from importlib import import_module
from typing import List, Set, Tuple, Type

from flask_restful import Api, Resource


class AppResource(Resource):
    @classmethod
    @abstractmethod
    def get_path(cls) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get_dependencies(cls) -> Set[str]:
        raise NotImplementedError


def get_resources(module) -> Tuple[List[Type[AppResource]], Set[str]]:
    resources, dependencies = [], set()
    for _, cls in inspect.getmembers(module, inspect.isclass):
        if inspect.getmodule(cls) is not module:
            continue
        if not issubclass(cls, AppResource):
            if issubclass(cls, Resource):
                raise ValueError
            continue
        resources.append(cls)
        dependencies.update(cls.get_dependencies())
    return resources, dependencies


def add_resources(api: Api, resources: List[Type[AppResource]]):
    for resource in resources:
        if resource in api.resources:
            raise ValueError
        if resource.get_path() in api.urls:
            raise ValueError
        api.add_resource(resource, resource.get_path())


def add_resources_from(api: Api, module_name: str):
    module = import_module(module_name)
    resources, dep_paths = get_resources(module)
    del module

    add_resources(api, resources)
    del resources

    seen_dep_paths = set()
    while len(dep_paths) > 0:
        dep_path = dep_paths.pop()

        assert dep_path not in seen_dep_paths

        if dep_path == module_name:
            raise ValueError
        seen_dep_paths.add(dep_path)

        dep_module = import_module(dep_path)
        resources, _dep_paths = get_resources(dep_module)
        del dep_module

        add_resources(api, resources)
        del resources

        _dep_paths.difference_update()
        dep_paths.update(_dep_paths)
        del _dep_paths
