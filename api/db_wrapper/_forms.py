import datetime
import enum
from abc import ABC, abstractmethod

import peewee
from werkzeug.exceptions import BadRequest, Conflict, NotFound

from db.models import auth, forms


class Form(ABC):
    _db_model: forms.Form = None

    def __init__(self, _id: int = None):
        self._form = None

        if _id is not None:
            try:
                self._form = self._db_model.get_by_id(_id)
            except self._db_model.DoesNotExist:
                raise NotFound("form not found")

    def create(self, user: auth.User, **kwargs) -> int:
        if self._form is not None:
            # This is indeed an internal server error.
            raise Exception("instantiated form can't create other")

        self._validate_kwargs(**kwargs)

        creation_kwargs = self._convert_kwarg_values(**kwargs)

        try:
            self._form = self._db_model.create(user=user, **creation_kwargs)
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


class PatientInformation(Form):
    _db_model: forms.Form = forms.PatientInformation

    def _serialized(self):
        return dict(
            id=self._form.id,
            user_id=self._form.user.id,
            gender=self._form.gender.value,
            birthday=self._form.birthday.isoformat(),
            acquaintance_phone=self._form.acquaintance_phone,
            address=self._form.address,
            neighborhood=self._form.neighborhood,
            city=self._form.city,
            country=self._form.country,
            updated_at=None
            if self._form.updated_at is None
            else self._form.updated_at.isoformat(),
            created_at=None
            if self._form.created_at is None
            else self._form.created_at.isoformat(),
        )

    def _convert_kwarg_values(self, **kwargs):
        if "gender" in kwargs:
            kwargs["gender"] = self._db_model.GenderTypes(kwargs["gender"])

        if "birthday" in kwargs:
            kwargs["birthday"] = datetime.date.fromisoformat(kwargs["birthday"])

        return kwargs

    def _validate_kwargs(self, **kwargs):
        valid_kwargs = {
            "gender",
            "birthday",
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
            gender_types = set(gender.value for gender in self._db_model.GenderTypes)
            if kwargs["gender"] not in gender_types:
                raise BadRequest("invalid gender")

        if "birthday" in kwargs:
            try:
                _ = datetime.date.fromisoformat(kwargs["birthday"])
            except ValueError:
                raise BadRequest("birthday date is malformed")


class SociodemographicEvaluation(Form):
    _db_model = forms.SociodemographicEvaluation

    def _convert_kwarg_values(self, **kwargs):
        if "civil_status" in kwargs:
            kwargs["civil_status"] = self._db_model.CivilStatusTypes(
                kwargs["civil_status"]
            )

        if "lives_with_status" in kwargs:
            kwargs["lives_with_status"] = self._db_model.LivesWithStatusTypes(
                kwargs["lives_with_status"]
            )

        if "education" in kwargs:
            kwargs["education"] = self._db_model.EducationTypes(kwargs["education"])

        if "occupational_status" in kwargs:
            kwargs["occupational_status"] = self._db_model.OccupationalStatusTypes(
                kwargs["occupational_status"]
            )

        return kwargs

    def _serialized(self):
        return dict(
            id=self._form.id,
            user_id=self._form.user.id,
            civil_status=self._form.civil_status.value,
            lives_with_status=self._form.lives_with_status.value,
            education=self._form.education.value,
            occupational_status=self._form.occupational_status.value,
            current_job=self._form.current_job,
            last_job=self._form.last_job,
            is_sick=self._form.is_sick,
            diseases=self._form.diseases,
            is_medicated=self._form.is_medicated,
            medicines=self._form.medicines,
            updated_at=None
            if self._form.updated_at is None
            else self._form.updated_at.isoformat(),
            created_at=None
            if self._form.created_at is None
            else self._form.created_at.isoformat(),
        )

    def _validate_kwargs(self, **kwargs):
        valid_kwargs = {
            "civil_status",
            "lives_with_status",
            "education",
            "occupational_status",
            "current_job",
            "last_job",
            "is_sick",
            "diseases",
            "is_medicated",
            "medicines",
        }
        for kwarg in kwargs.keys():
            if kwarg not in valid_kwargs:
                # This is indeed an internal server error.
                raise TypeError(f"{kwarg} is not a valid keyword argument")

        if "civil_status" in kwargs:
            civil_status_types = set(
                civil_status.value for civil_status in self._db_model.CivilStatusTypes
            )
            if kwargs["civil_status"] not in civil_status_types:
                raise BadRequest("invalid civil_status")

        if "lives_with_status" in kwargs:
            lives_with_status_types = set(
                lives_with_status.value
                for lives_with_status in self._db_model.LivesWithStatusTypes
            )
            if kwargs["lives_with_status"] not in lives_with_status_types:
                raise BadRequest("invalid lives_with_status")

        if "education" in kwargs:
            education_types = set(
                education.value for education in self._db_model.EducationTypes
            )
            if kwargs["education"] not in education_types:
                raise BadRequest("invalid education")

        if "occupational_status" in kwargs:
            occupational_status_types = set(
                occupational_status.value
                for occupational_status in self._db_model.OccupationalStatusTypes
            )
            if kwargs["occupational_status"] not in occupational_status_types:
                raise BadRequest("invalid occupational_status")

        if "diseases" in kwargs:
            if not all(isinstance(disease, str) for disease in kwargs["diseases"]):
                raise BadRequest("invalid disease value")

        if "medicines" in kwargs:
            if not all(isinstance(medicine, str) for medicine in kwargs["medicines"]):
                raise BadRequest("invalid medicine value")


class KineticFunctionalEvaluation(Form):
    _db_model = forms.KineticFunctionalEvaluation

    def _convert_kwarg_values(self, **kwargs):
        if "structure_and_function" in kwargs:
            structure_and_function = self._db_model.StructureAndFunctionTypes(0)
            for string in kwargs["structure_and_function"]:
                structure_and_function |= self._db_model.StructureAndFunctionTypes.from_string(
                    string
                )
            kwargs["structure_and_function"] = structure_and_function

        if "activity_and_participation" in kwargs:
            activity_and_participation = self._db_model.ActivityAndParticipationTypes(0)
            for string in kwargs["activity_and_participation"]:
                activity_and_participation |= self._db_model.ActivityAndParticipationTypes.from_string(
                    string
                )
            kwargs["activity_and_participation"] = activity_and_participation

        return kwargs

    def _serialized(self):
        structure_and_function = list()
        for enum_item in self._db_model.StructureAndFunctionTypes:
            if self._form.structure_and_function & enum_item:
                structure_and_function.append(
                    self._db_model.StructureAndFunctionTypes.to_string(enum_item)
                )

        activity_and_participation = list()
        for enum_item in self._db_model.ActivityAndParticipationTypes:
            if self._form.activity_and_participation & enum_item:
                activity_and_participation.append(
                    self._db_model.ActivityAndParticipationTypes.to_string(enum_item)
                )

        return dict(
            id=self._form.id,
            user_id=self._form.user.id,
            clinic_diagnostic=self._form.clinic_diagnostic,
            main_complaint=self._form.main_complaint,
            functional_complaint=self._form.functional_complaint,
            clinical_history=self._form.clinical_history,
            functional_history=self._form.functional_history,
            structure_and_function=structure_and_function,
            activity_and_participation=activity_and_participation,
            physical_functional_tests_results=self._form.physical_functional_tests_results,
            complementary_exams_results=self._form.complementary_exams_results,
            deficiency_diagnosis=self._form.deficiency_diagnosis,
            activity_limitation_diagnosis=self._form.activity_limitation_diagnosis,
            participation_restriction_diagnosis=self._form.participation_restriction_diagnosis,
            environment_factors_diagnosis=self._form.environment_factors_diagnosis,
            functional_objectives_diagnosis=self._form.functional_objectives_diagnosis,
            therapeutic_plan_diagnosis=self._form.therapeutic_plan_diagnosis,
            reevaluation_dates=self._form.reevaluation_dates,
            academic_assessor=self._form.academic_assessor,
            preceptor_assessor=self._form.preceptor_assessor,
            updated_at=None
            if self._form.updated_at is None
            else self._form.updated_at.isoformat(),
            created_at=None
            if self._form.created_at is None
            else self._form.created_at.isoformat(),
        )

    def _validate_kwargs(self, **kwargs):
        valid_kwargs = {
            "clinic_diagnostic",
            "main_complaint",
            "functional_complaint",
            "clinical_history",
            "functional_history",
            "structure_and_function",
            "activity_and_participation",
            "physical_functional_tests_results",
            "complementary_exams_results",
            "deficiency_diagnosis",
            "activity_limitation_diagnosis",
            "participation_restriction_diagnosis",
            "environment_factors_diagnosis",
            "functional_objectives_diagnosis",
            "therapeutic_plan_diagnosis",
            "reevaluation_dates",
            "academic_assessor",
            "preceptor_assessor",
        }
        for kwarg in kwargs.keys():
            if kwarg not in valid_kwargs:
                # This is indeed an internal server error.
                raise TypeError(f"{kwarg} is not a valid keyword argument")

        if "structure_and_function" in kwargs:
            valid_strings = (
                self._db_model.StructureAndFunctionTypes.valid_string_values()
            )
            if not all(
                string in valid_strings for string in kwargs["structure_and_function"]
            ):
                raise BadRequest("invalid structure_and_function value")

        if "activity_and_participation" in kwargs:
            valid_strings = (
                self._db_model.ActivityAndParticipationTypes.valid_string_values()
            )
            if not all(
                string in valid_strings
                for string in kwargs["activity_and_participation"]
            ):
                raise BadRequest("invalid activity_and_participation value")

        if "functional_objectives_diagnosis" in kwargs:
            if not all(
                isinstance(medicine, str)
                for medicine in kwargs["functional_objectives_diagnosis"]
            ):
                raise BadRequest("invalid functional objective value")

        if "therapeutic_plan_diagnosis" in kwargs:
            if not all(
                isinstance(medicine, str)
                for medicine in kwargs["therapeutic_plan_diagnosis"]
            ):
                raise BadRequest("invalid therapeutic plan value")

        if "reevaluation_dates" in kwargs:
            if not all(
                isinstance(reevaluation_date, str)
                for reevaluation_date in kwargs["reevaluation_dates"]
            ):
                raise BadRequest("invalid reevaluate date value")

            for reevaluation_date in kwargs["reevaluation_dates"]:
                try:
                    _ = datetime.date.fromisoformat(reevaluation_date)
                except ValueError:
                    raise BadRequest("reevaluate date is malformed")


class FormTypes(enum.Enum):
    PatientInformation = "patient_information"
    SociodemographicEvaluation = "sociodemographic_evaluation"
    KineticFunctionalEvaluation = "kinetic_functional_evaluation"
