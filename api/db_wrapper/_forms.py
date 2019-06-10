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
        birthday: str,
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
            acquaintance_phone=acquaintance_phone,
            address=address,
            neighborhood=neighborhood,
            city=city,
            country=country,
        )

        creation_kwargs = self._convert_kwarg_values(
            gender=gender,
            birthday=birthday,
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
            id=self._patient_information.id,
            user_id=self._patient_information.user.id,
            gender=self._patient_information.gender.value,
            birthday=self._patient_information.birthday.isoformat(),
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
        if "gender" in kwargs:
            kwargs["gender"] = forms.PatientInformation.GenderTypes(kwargs["gender"])

        if "birthday" in kwargs:
            kwargs["birthday"] = datetime.date.fromisoformat(kwargs["birthday"])

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
            gender_types = set(
                gender.value for gender in forms.PatientInformation.GenderTypes
            )
            if kwargs["gender"] not in gender_types:
                raise BadRequest("invalid gender")

        if "birthday" in kwargs:
            try:
                _ = datetime.date.fromisoformat(kwargs["birthday"])
            except ValueError:
                raise BadRequest("birthday date is malformed")


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


class SociodemographicEvaluation(Form):
    _db_model = forms.SociodemographicEvaluation

    def _convert_kwarg_values(self, **kwargs):
        if "civil_status" in kwargs:
            kwargs["civil_status"] = forms.SociodemographicEvaluation.CivilStatusTypes(
                kwargs["civil_status"]
            )

        if "lives_with_status" in kwargs:
            kwargs[
                "lives_with_status"
            ] = forms.SociodemographicEvaluation.LivesWithStatusTypes(
                kwargs["lives_with_status"]
            )

        if "education" in kwargs:
            kwargs["education"] = forms.SociodemographicEvaluation.EducationTypes(
                kwargs["education"]
            )

        if "occupational_status" in kwargs:
            kwargs[
                "occupational_status"
            ] = forms.SociodemographicEvaluation.OccupationalStatusTypes(
                kwargs["occupational_status"]
            )

        return kwargs

    def _serialized(self):
        return dict(
            id=self._form.id,
            patient_information_id=self._form.patient_information.id,
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
                civil_status.value
                for civil_status in forms.SociodemographicEvaluation.CivilStatusTypes
            )
            if kwargs["civil_status"] not in civil_status_types:
                raise BadRequest("invalid civil_status")

        if "lives_with_status" in kwargs:
            lives_with_status_types = set(
                lives_with_status.value
                for lives_with_status in forms.SociodemographicEvaluation.LivesWithStatusTypes
            )
            if kwargs["lives_with_status"] not in lives_with_status_types:
                raise BadRequest("invalid lives_with_status")

        if "education" in kwargs:
            education_types = set(
                education.value
                for education in forms.SociodemographicEvaluation.EducationTypes
            )
            if kwargs["education"] not in education_types:
                raise BadRequest("invalid education")

        if "occupational_status" in kwargs:
            occupational_status_types = set(
                occupational_status.value
                for occupational_status in forms.SociodemographicEvaluation.OccupationalStatusTypes
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
            structure_and_function = forms.KineticFunctionalEvaluation.StructureAndFunctionTypes(
                0
            )
            for string in kwargs["structure_and_function"]:
                structure_and_function |= forms.KineticFunctionalEvaluation.StructureAndFunctionTypes.from_string(
                    string
                )
            kwargs["structure_and_function"] = structure_and_function

        if "activity_and_participation" in kwargs:
            activity_and_participation = forms.KineticFunctionalEvaluation.ActivityAndParticipationTypes(
                0
            )
            for string in kwargs["activity_and_participation"]:
                activity_and_participation |= forms.KineticFunctionalEvaluation.ActivityAndParticipationTypes.from_string(
                    string
                )
            kwargs["activity_and_participation"] = activity_and_participation

        return kwargs

    def _serialized(self):
        structure_and_function = list()
        for enum_item in forms.KineticFunctionalEvaluation.StructureAndFunctionTypes:
            if self._form.structure_and_function & enum_item:
                structure_and_function.append(
                    forms.KineticFunctionalEvaluation.StructureAndFunctionTypes.to_string(
                        enum_item
                    )
                )

        activity_and_participation = list()
        for (
            enum_item
        ) in forms.KineticFunctionalEvaluation.ActivityAndParticipationTypes:
            if self._form.activity_and_participation & enum_item:
                activity_and_participation.append(
                    forms.KineticFunctionalEvaluation.ActivityAndParticipationTypes.to_string(
                        enum_item
                    )
                )

        return dict(
            id=self._form.id,
            patient_information_id=self._form.patient_information.id,
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
                forms.KineticFunctionalEvaluation.StructureAndFunctionTypes.valid_string_values()
            )
            if not all(
                string in valid_strings for string in kwargs["structure_and_function"]
            ):
                raise BadRequest("invalid structure_and_function value")

        if "activity_and_participation" in kwargs:
            valid_strings = (
                forms.KineticFunctionalEvaluation.ActivityAndParticipationTypes.valid_string_values()
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
    SociodemographicEvaluation = "sociodemographic_evaluation"
    KineticFunctionalEvaluation = "kinetic_functional_evaluation"
