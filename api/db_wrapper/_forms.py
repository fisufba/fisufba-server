import datetime
import enum
from abc import ABC, abstractmethod

import peewee
from werkzeug.exceptions import BadRequest, Conflict, NotFound

from db.models import forms


class Form(ABC):
    _db_model: forms.Form = None

    def __init__(self, _id: int = None):
        self._form = None

        if _id is not None:
            try:
                self._form = self._db_model.get(id=_id)
            except self._db_model.DoesNotExist:
                raise NotFound("Form not found")

    def create(self, **kwargs):
        if self._form is not None:
            raise Conflict("Form already exists")

        self._validate_kwargs(**kwargs)

        #: TODO PatientInformation.
        try:
            self._form = self._db_model.create(**kwargs)
        except peewee.IntegrityError:
            raise Conflict("Form already exists")

    def update(self, **kwargs):
        if self._form is None:
            raise BadRequest("Form was not instantiated")

        self._validate_kwargs(**kwargs)

        #: TODO PatientInformation.
        query = self._db_model.update(
            **kwargs, updated_at=datetime.datetime.utcnow()
        ).where(self._db_model.id == self._form.id)
        if query.execute() == 0:
            # This is indeed an internal server error.
            raise Exception("Login Failed")

    def serialized(self):
        #: TODO PatientInformation.
        return self._serialized(dict())

    @abstractmethod
    def _serialized(self, serialized_form: dict):
        raise NotImplementedError

    @abstractmethod
    def _validate_kwargs(self, **kwargs):
        raise NotImplementedError


class FormTypes(enum.Enum):
    pass
