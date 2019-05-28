import enum
import json
from typing import Any

from peewee import CharField
from peewee import TextField


class EnumField(CharField):
    """This class enables an Enum like field for Peewee.

    See Also: https://github.com/coleifer/peewee/issues/630.

    """

    def __init__(self, choices: enum.EnumMeta, *args: Any, **kwargs: Any) -> None:
        super(CharField, self).__init__(*args, **kwargs)
        self.choices = choices
        self.max_length = 255

    def db_value(self, value: Any) -> Any:
        return value.value

    def python_value(self, value: Any) -> Any:
        cast = type(list(self.choices)[0])
        assert all(isinstance(choice, cast) for choice in list(self.choices))
        return self.choices(cast(value))


class JSONField(TextField):
    """This class enables a JSON like field for Peewee.

    """

    def db_value(self, value) -> str:
        return json.dumps(value)

    def python_value(self, value) -> Any:
        if value is not None:
            return json.loads(value)
        return None
