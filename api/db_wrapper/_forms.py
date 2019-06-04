import datetime
import enum
from abc import ABC, abstractmethod

import peewee
from werkzeug.exceptions import BadRequest, Conflict, NotFound

from db.models import auth, forms


class PatientInformation:
    def __init__(self, _id: int = None):
        self._patient_information = None

        if _id is not None:
            try:
                self._patient_information = forms.PatientInformation.get_by_id(_id)
            except forms.PatientInformation.DoesNotExist:
                raise NotFound("patient information not found")

    def create(
        self,
        user: auth.User,
        gender: str,
        birthday: datetime.datetime,
        phone: str,
        acquaintance_phone: str,
        address: str,
        neighborhood: str,
        city: str,
        country: str,
    ) -> int:
        if self._patient_information is not None:
            raise Conflict("patient information already exists")

        self._validate_kwargs(
            gender=gender,
            birthday=birthday,
            phone=phone,
            acquaintance_phone=acquaintance_phone,
            address=address,
            neighborhood=neighborhood,
            city=city,
            country=country,
        )

        creation_kwargs = self._convert_kwarg_values(
            gender=gender,
            birthday=birthday,
            phone=phone,
            acquaintance_phone=acquaintance_phone,
            address=address,
            neighborhood=neighborhood,
            city=city,
            country=country,
        )

        try:
            self._patient_information = forms.PatientInformation.create(
                user=user, **creation_kwargs
            )
        except peewee.IntegrityError:
            raise Conflict("patient information already exists")

        return self._patient_information.id

    def serialized(self) -> dict:
        if self._patient_information is None:
            # This is indeed an internal server error.
            raise Exception("patient information was not properly instantiated")

        return dict(
            user_id=self._patient_information.user.id,
            gender=self._patient_information.gender.value,
            birthday=self._patient_information.birthday.isoformat(),
            phone=self._patient_information.phone,
            acquaintance_phone=self._patient_information.acquaintance_phone,
            address=self._patient_information.address,
            neighborhood=self._patient_information.neighborhood,
            city=self._patient_information.city,
            country=self._patient_information.country,
            updated_at=None
            if self._patient_information.updated_at is None
            else self._patient_information.updated_at.isoformat(),
            created_at=None
            if self._patient_information.created_at is None
            else self._patient_information.created_at.isoformat(),
        )

    def update(self, **kwargs):
        if self._patient_information is None:
            # This is indeed an internal server error.
            raise Exception("patient information was not properly instantiated")

        self._validate_kwargs(**kwargs)

        update_kwargs = self._convert_kwarg_values(**kwargs)

        query = forms.PatientInformation.update(
            **update_kwargs, updated_at=datetime.datetime.utcnow()
        ).where(forms.PatientInformation.id == self._patient_information.id)
        if query.execute() == 0:
            # This is indeed an internal server error.
            raise Exception("update failed")

        self._restore()

    def _convert_kwarg_values(self, **kwargs):
        self._validate_kwargs(**kwargs)

        if "gender" in kwargs:
            kwargs["gender"] = forms.PatientInformation.GenderTypes(kwargs["gender"])

        return kwargs

    def _restore(self):
        if self._patient_information is None:
            # This is indeed an internal server error.
            raise Exception("patient information was not properly instantiated")

        try:
            self._patient_information = forms.PatientInformation.get_by_id(
                self._patient_information.id
            )
        except forms.PatientInformation.DoesNotExist:
            # This is indeed an internal server error.
            raise Exception("patient information does not exist")

    def _validate_kwargs(self, **kwargs):
        valid_kwargs = {
            "gender",
            "birthday",
            "phone",
            "acquaintance_phone",
            "address",
            "neighborhood",
            "city",
            "country",
        }
        for kwarg in kwargs.keys():
            if kwarg not in valid_kwargs:
                # This is indeed an internal server error.
                raise TypeError(f"{kwarg} is not a valid keyword argument")

        if "gender" in kwargs:
            genders = set(
                gender.value for gender in forms.PatientInformation.GenderTypes
            )
            if kwargs["gender"] not in genders:
                raise BadRequest("invalid gender")


class Form(ABC):
    _db_model: forms.Form = None

    def __init__(self, _id: int = None):
        self._form = None

        if _id is not None:
            try:
                self._form = self._db_model.get_by_id(_id)
            except self._db_model.DoesNotExist:
                raise NotFound("form not found")

    def create(self, patient_information: forms.PatientInformation, **kwargs) -> int:
        if self._form is not None:
            raise Conflict("form already exists")

        self._validate_kwargs(**kwargs)

        creation_kwargs = self._convert_kwarg_values(**kwargs)

        try:
            self._form = self._db_model.create(
                patient_information=patient_information, **creation_kwargs
            )
        except peewee.IntegrityError:
            raise Conflict("form already exists")

        return self._form.id

    def serialized(self) -> dict:
        if self._form is None:
            # This is indeed an internal server error.
            raise Exception("form was not properly instantiated")

        return self._serialized()

    def update(self, **kwargs):
        if self._form is None:
            # This is indeed an internal server error.
            raise Exception("form was not properly instantiated")

        self._validate_kwargs(**kwargs)

        update_kwargs = self._convert_kwarg_values(**kwargs)

        query = self._db_model.update(
            **update_kwargs, updated_at=datetime.datetime.utcnow()
        ).where(self._db_model.id == self._form.id)
        if query.execute() == 0:
            # This is indeed an internal server error.
            raise Exception("update failed")

        self._restore()

    @abstractmethod
    def _convert_kwarg_values(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def _serialized(self) -> dict:
        raise NotImplementedError

    def _restore(self):
        if self._form is None:
            # This is indeed an internal server error.
            raise Exception("form was not properly instantiated")

        try:
            self._form = self._db_model.get_by_id(self._form.id)
        except self._db_model.DoesNotExist:
            # This is indeed an internal server error.
            raise Exception("form does not exist")

    @abstractmethod
    def _validate_kwargs(self, **kwargs):
        raise NotImplementedError


class FormTypes(enum.Enum):
    SociodemographicEvaluation = "sociodemographicevaluation"
    KineticFunctionalEvaluation = "kineticfunctionalevaluation"
