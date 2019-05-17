from abc import abstractmethod
from typing import Set

from flask_restful import Resource


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
