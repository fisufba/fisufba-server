from flask import g, request, url_for
from werkzeug.exceptions import BadRequest

from api.abc import AppResource
from api.abc import authentication_required
from api.db_wrapper import FormTypes
from _datetime import datetime


class FormsIndex(AppResource):
    """AppResource responsible for the Forms index of an Api.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Returns:
            An url path.

        """
        return "/forms"

    @classmethod
    def get_dependencies(cls):
        """Returns the dependencies of this AppResource.

        Notes:
            If there's no dependency this must return an empty set.

        Returns:
            A set of module names that contains AppResource
                classes used by this AppResource.

        """
        return set()

    def get(self):
        """Treats HTTP GET requests.

        It shows the possible paths to follow.

        Notes:
            For better understanding, refer: http://stateless.co/hal_specification.html.

        Returns:
            Dict object following the HAL format.

        """
        return {
            "_links": {
                "self": {"href": url_for("formsindex")},
                "curies": [{"name": "forms", "href": "TODO/{rel}", "templated": True}],
                "forms:_sociodemographicevaluation": {
                    "href": url_for("_sociodemographicevaluation"),
                    "templated": True,
                },
                "forms:_sociodemographicevaluationview": {
                    "href": url_for("_sociodemographicevaluationview", form_id=0),
                    "templated": True,
                },
                "forms:kineticfunctionalevaluation": {
                    "href": url_for("_kineticfunctionalevaluation"),
                    "templated": True,
                },
                "forms:kineticfunctionalevaluationview": {
                    "href": url_for("_kineticfunctionalevaluationview", form_id=0),
                    "templated": True,
                },
            }
        }


class _SociodemographicEvaluation(AppResource):
    """AppResource responsible for SociodemographicEvaluation form creation.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Raises:
            NotImplementedError: When not implemented by AppResource's children.

        Returns:
            An url path.

        """
        return "/forms/sociodemographicevaluation"

    @classmethod
    def get_dependencies(cls):
        """Returns the dependencies of this AppResource.

        Notes:
            If there's no dependency this must return an empty set.

        Raises:
            NotImplementedError: When not implemented by AppResource's children.

        Returns:
            A set of module names that contains AppResource
                classes used by this AppResource.

        """
        return set()

    @authentication_required
    def post(self):
        post_body = request.get_json()

        try:
            patient_information_id = post_body["patient_information_id"]
        except KeyError:
            raise BadRequest("patient_information_id field is missing")

        try:
            civil_status = post_body["civil_status"]
        except KeyError:
            raise BadRequest("civil_status field is missing")

        try:
            lives_with_status = post_body["lives_with_status"]
        except KeyError:
            raise BadRequest("lives_with_status field is missing")

        try:
            education = post_body["education"]
        except KeyError:
            raise BadRequest("education field is missing")

        try:
            occupational_status = post_body["occupational_status"]
        except KeyError:
            raise BadRequest("occupational_status field is missing")

        try:
            current_job = post_body["current_job"]
        except KeyError:
            raise BadRequest("current_job field is missing")

        try:
            last_job = post_body["last_job"]
        except KeyError:
            raise BadRequest("last_job field is missing")

        try:
            is_sick = post_body["is_sick"]
        except KeyError:
            raise BadRequest("is_sick field is missing")

        try:
            diseases = post_body["diseases"]
        except KeyError:
            raise BadRequest("diseases field is missing")

        try:
            is_medicated = post_body["is_medicated"]
        except KeyError:
            raise BadRequest("is_medicated field is missing")

        try:
            medicines = post_body["medicines"]
        except KeyError:
            raise BadRequest("medicines field is missing")

        if not isinstance(patient_information_id, int):
            raise BadRequest("patient_information_id is not an integer")
        if not isinstance(civil_status, str):
            raise BadRequest("civil_status is not a string")
        if not isinstance(lives_with_status, str):
            raise BadRequest("lives_with_status is not a string")
        if not isinstance(education, str):
            raise BadRequest("education is not a string")
        if not isinstance(occupational_status, str):
            raise BadRequest("occupational_status is not a string")
        if current_job is not None and not isinstance(current_job, str):
            raise BadRequest("current_job is not a string")
        if last_job is not None and not isinstance(last_job, str):
            raise BadRequest("last_job is not a string")
        if not isinstance(is_sick, bool):
            raise BadRequest("is_sick is not a boolean")
        if diseases is not None and not isinstance(diseases, list):
            raise BadRequest("diseases is not a list")
        if not isinstance(is_medicated, bool):
            raise BadRequest("is_medicated field is not a boolean")
        if medicines is not None and not isinstance(medicines, list):
            raise BadRequest("medicines field is not a list")

        form_id = g.session.user.create_form(
            FormTypes("sociodemographic_evaluation"),
            patient_information_id=patient_information_id,
            civil_status=civil_status,
            lives_with_status=lives_with_status,
            education=education,
            occupational_status=occupational_status,
            current_job=current_job,
            last_job=last_job,
            is_sick=is_sick,
            diseases=diseases,
            is_medicated=is_medicated,
            medicines=medicines,
        )

        return {
            "_links": {"self": {"href": url_for("_sociodemographicevaluation")}},
            "form_id": form_id,
        }


class _SociodemographicEvaluationView(AppResource):
    """AppResource responsible for read and update SociodemographicEvaluation form information.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Raises:
            NotImplementedError: When not implemented by AppResource's children.

        Returns:
            An url path.

        """
        return "/forms/sociodemographicevaluation/<int:form_id>"

    @classmethod
    def get_dependencies(cls):
        """Returns the dependencies of this AppResource.

        Notes:
            If there's no dependency this must return an empty set.

        Raises:
            NotImplementedError: When not implemented by AppResource's children.

        Returns:
            A set of module names that contains AppResource
                classes used by this AppResource.

        """
        return set()

    @authentication_required
    def get(self, form_id: int):
        return {
            "_links": {"self": {"href": url_for("_forms", form_id=form_id)}},
            "form": g.session.user.get_serialized_form(
                form_t=FormTypes("sociodemographic_evaluation"), form_id=form_id
            ),
        }

    @authentication_required
    def patch(self, form_id: int):
        patch_body = request.get_json()

        kwargs = {}

        if "civil_status" in patch_body:
            civil_status = patch_body["civil_status"]
            if not isinstance(civil_status, str):
                raise BadRequest("civil_status is not a string")
            kwargs["civil_status"] = civil_status

        if "lives_with_status" in patch_body:
            lives_with_status = patch_body["lives_with_status"]
            if not isinstance(lives_with_status, str):
                raise BadRequest("lives_with_status is not a string")
            kwargs["lives_with_status"] = lives_with_status

        if "education" in patch_body:
            education = patch_body["education"]
            if not isinstance(education, str):
                raise BadRequest("education is not a string")
            kwargs["education"] = education

        if "occupational_status" in patch_body:
            occupational_status = patch_body["occupational_status"]
            if not isinstance(occupational_status, str):
                raise BadRequest("occupational_status is not a string")
            kwargs["occupational_status"] = occupational_status

        if "current_job" in patch_body:
            current_job = patch_body["current_job"]
            if current_job is not None and not isinstance(current_job, str):
                raise BadRequest("current_job is not a string")
            kwargs["current_job"] = current_job

        if "last_job" in patch_body:
            last_job = patch_body["last_job"]
            if last_job is not None and not isinstance(last_job, str):
                raise BadRequest("last_job is not a string")
            kwargs["last_job"] = last_job

        if "is_sick" in patch_body:
            is_sick = patch_body["is_sick"]
            if not isinstance(is_sick, bool):
                raise BadRequest("is_sick is not a boolean")
            kwargs["is_sick"] = is_sick

        if "diseases" in patch_body:
            diseases = patch_body["diseases"]
            if not isinstance(diseases, list):
                raise BadRequest("diseases is not a list")
            kwargs["diseases"] = diseases

        if "is_medicated" in patch_body:
            is_medicated = patch_body["is_medicated"]
            if not isinstance(is_medicated, bool):
                raise BadRequest("is_medicated is not a boolean")
            kwargs["is_medicated"] = is_medicated

        if "medicines" in patch_body:
            medicines = patch_body["medicines"]
            if medicines is not None and not isinstance(medicines, list):
                raise BadRequest("medicines is not a list")
            kwargs["medicines"] = medicines

        g.session.user.update_form(
            form_t=FormTypes("sociodemographic_evaluation"), form_id=form_id, **kwargs
        )

        return {
            "_links": {
                "self": {
                    "href": url_for("_sociodemographicevaluationview", form_id=form_id)
                }
            },
            "form_id": form_id,
        }


class _KineticFunctionalEvaluation(AppResource):
    """AppResource responsible for KineticFunctionalEvaluation form creation.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Raises:
            NotImplementedError: When not implemented by AppResource's children.

        Returns:
            An url path.

        """
        return "/forms/kineticfunctionalevaluation"

    @classmethod
    def get_dependencies(cls):
        """Returns the dependencies of this AppResource.

        Notes:
            If there's no dependency this must return an empty set.

        Raises:
            NotImplementedError: When not implemented by AppResource's children.

        Returns:
            A set of module names that contains AppResource
                classes used by this AppResource.

        """
        return set()

    @authentication_required
    def post(self):
        post_body = request.get_json()

        try:
            user_id = post_body["user_id"]
        except KeyError:
            raise BadRequest("user_id field is missing")

        try:
            medical_record_number = post_body["medical_record_number"]
        except KeyError:
            raise BadRequest("medical_record_number field is missing")

        try:
            evaluation_date = post_body["evaluation_date"]
        except KeyError:
            raise BadRequest("evaluation_date field is missing")

        try:
            clinic_diagnostic = post_body["clinic_diagnostic"]
        except KeyError:
            raise BadRequest("clinic_diagnostic field is missing")

        try:
            main_complaint = post_body["main_complaint"]
        except KeyError:
            raise BadRequest("main_complaint field is missing")

        try:
            functional_complaint = post_body["functional_complaint"]
        except KeyError:
            raise BadRequest("functional_complaint field is missing")

        try:
            clinical_history = post_body["clinical_history"]
        except KeyError:
            raise BadRequest("clinical_history field is missing")

        try:
            functional_history = post_body["functional_history"]
        except KeyError:
            raise BadRequest("functional_history field is missing")

        structure_and_function = post_body.get("structure_and_function", None)

        activity_and_participation = post_body.get("activity_and_participation", None)

        physical_functional_tests_results = post_body.get(
            "physical_functional_tests_results", None
        )

        complementary_exams_results = post_body.get("complementary_exams_results", None)

        deficiency_diagnosis = post_body.get("deficiency_diagnosis", None)

        activity_limitation_diagnosis = post_body.get(
            "activity_limitation_diagnosis", None
        )

        participation_restriction_diagnosis = post_body.get(
            "participation_restriction_diagnosis", None
        )

        environment_factors_diagnosis = post_body.get(
            "environment_factors_diagnosis", None
        )

        functional_objectives_diagnosis = post_body.get(
            "functional_objectives_diagnosis", None
        )

        therapeutic_plan_diagnosis = post_body.get("therapeutic_plan_diagnosis", None)

        reevaluation_dates = post_body.get("reevaluation_dates", None)

        academic_assessor = post_body.get("academic_assessor", None)

        preceptor_assessor = post_body.get("preceptor_assessor", None)

        if not isinstance(user_id, int):
            raise BadRequest("user_id field is not an integer")
        if not isinstance(medical_record_number, int):
            raise BadRequest("medical_record_number field is not an integer")
        if not isinstance(evaluation_date, str):
            raise BadRequest("evaluation_date field is not a string")
        if not isinstance(clinic_diagnostic, str):
            raise BadRequest("clinic_diagnostic field is not a string")
        if not isinstance(main_complaint, str):
            raise BadRequest("main_complaint field is not a string")
        if not isinstance(functional_complaint, str):
            raise BadRequest("functional_complaint field is not a string")
        if not isinstance(clinical_history, str):
            raise BadRequest("clinical_history field is not a string")
        if not isinstance(functional_history, str):
            raise BadRequest("functional_history field is not a string")
        if structure_and_function is not None and not isinstance(
            structure_and_function, str
        ):
            raise BadRequest("structure_and_function field is not a string")
        if activity_and_participation is not None and not isinstance(
            activity_and_participation, str
        ):
            raise BadRequest("activity_and_participation field is not a string")
        if physical_functional_tests_results is not None and not isinstance(
            physical_functional_tests_results, str
        ):
            raise BadRequest("physical_functional_tests_results field is not a string")
        if complementary_exams_results is not None and not isinstance(
            complementary_exams_results, str
        ):
            raise BadRequest("complementary_exams_results field is not a string")
        if deficiency_diagnosis is not None and not isinstance(
            deficiency_diagnosis, str
        ):
            raise BadRequest("deficiency_diagnosis field is not a string")
        if activity_limitation_diagnosis is not None and not isinstance(
            activity_limitation_diagnosis, str
        ):
            raise BadRequest("activity_limitation_diagnosis field is not a string")
        if participation_restriction_diagnosis is not None and not isinstance(
            participation_restriction_diagnosis, str
        ):
            raise BadRequest(
                "participation_restriction_diagnosis field is not a string"
            )
        if environment_factors_diagnosis is not None and not isinstance(
            environment_factors_diagnosis, str
        ):
            raise BadRequest("environment_factors_diagnosis field is not an list")
        if functional_objectives_diagnosis is not None and not isinstance(
            functional_objectives_diagnosis, list
        ):
            raise BadRequest("functional_objectives_diagnosis field is not an list")
        if therapeutic_plan_diagnosis is not None and not isinstance(
            therapeutic_plan_diagnosis, list
        ):
            raise BadRequest("therapeutic_plan_diagnosis field is not an list")
        if reevaluation_dates is not None and not isinstance(reevaluation_dates, list):
            raise BadRequest("reevaluation_dates field is not an list")
        if academic_assessor is not None and not isinstance(academic_assessor, str):
            raise BadRequest("academic_assessor field is not an list")
        if preceptor_assessor is not None and not isinstance(preceptor_assessor, str):
            raise BadRequest("preceptor_assessor field is not an list")

        form_id = g.session.user.create_form(
            FormTypes("kineticfunctional"),
            user_id=user_id,
            medical_record_number=medical_record_number,
            evaluation_date=evaluation_date,
            clinic_diagnostic=clinic_diagnostic,
            main_complaint=main_complaint,
            functional_complaint=functional_complaint,
            clinical_history=clinical_history,
            functional_history=functional_history,
            structure_and_function=structure_and_function,
            activity_and_participation=activity_and_participation,
            physical_functional_tests_results=physical_functional_tests_results,
            complementary_exams_results=complementary_exams_results,
            deficiency_diagnosis=deficiency_diagnosis,
            activity_limitation_diagnosis=activity_limitation_diagnosis,
            participation_restriction_diagnosis=participation_restriction_diagnosis,
            environment_factors_diagnosis=environment_factors_diagnosis,
            functional_objectives_diagnosis=functional_objectives_diagnosis,
            therapeutic_plan_diagnosis=therapeutic_plan_diagnosis,
            reevaluation_dates=reevaluation_dates,
            academic_assessor=academic_assessor,
            preceptor_assessor=preceptor_assessor,
        )

        return {
            "_links": {"self": {"href": url_for("_kineticfunctionalevaluation")}},
            "form_id": form_id,
        }


class _KineticFunctionalEvaluationView(AppResource):
    """AppResource responsible for read and update KineticFunctionalEvaluation form information.

    """

    @classmethod
    def get_path(cls):
        """Returns the url path of this AppResource.

        Raises:
            NotImplementedError: When not implemented by AppResource's children.

        Returns:
            An url path.

        """
        return "/forms/kineticfunctionalevaluation/<int:form_id>"

    @classmethod
    def get_dependencies(cls):
        """Returns the dependencies of this AppResource.

        Notes:
            If there's no dependency this must return an empty set.

        Raises:
            NotImplementedError: When not implemented by AppResource's children.

        Returns:
            A set of module names that contains AppResource
                classes used by this AppResource.

        """
        return set()

    @authentication_required
    def get(self, form_id: int):
        return {
            "_links": {"self": {"href": url_for("_forms", form_id=form_id)}},
            "form": g.session.user.get_serialized_form(
                form_t=FormTypes("kineticfunctional"), form_id=form_id
            ),
        }

    @authentication_required
    def patch(self, form_id: int):
        patch_body = request.get_json()

        kwargs = {}

        if "user_id" in patch_body:
            user_id = patch_body["user_id"]
            if not isinstance(user_id, int):
                raise BadRequest("user_id field is not an integer")
            kwargs["user_id"] = user_id

        if "medical_record_number" in patch_body:
            medical_record_number = patch_body["medical_record_number"]
            if not isinstance(medical_record_number, int):
                raise BadRequest("medical_record_number field is not an integer")
            kwargs["medical_record_number"] = medical_record_number

        if "evaluation_date" in patch_body:
            evaluation_date = patch_body["evaluation_date"]
            if not isinstance(evaluation_date, str):
                raise BadRequest("evaluation_date field is not a string")
            kwargs["evaluation_date"] = datetime.strftime(
                evaluation_date, "%d/%m/%Y"
            ).isoformat()

        if "clinic_diagnostic" in patch_body:
            clinic_diagnostic = patch_body["clinic_diagnostic"]
            if not isinstance(clinic_diagnostic, str):
                raise BadRequest("clinic_diagnostic field is not a string")
            kwargs["clinic_diagnostic"] = clinic_diagnostic

        if "main_complaint" in patch_body:
            main_complaint = patch_body["main_complaint"]
            if not isinstance(main_complaint, str):
                raise BadRequest("main_complaint field is not a string")
            kwargs["main_complaint"] = main_complaint

        if "functional_complaint" in patch_body:
            functional_complaint = patch_body["functional_complaint"]
            if not isinstance(functional_complaint, str):
                raise BadRequest("functional_complaint field is not a string")
            kwargs["functional_complaint"] = functional_complaint

        if "clinical_history" in patch_body:
            clinical_history = patch_body["clinical_history"]
            if not isinstance(clinical_history, str):
                raise BadRequest("clinical_history field is not a string")
            kwargs["clinical_history"] = clinical_history

        if "functional_history" in patch_body:
            functional_history = patch_body["functional_history"]
            if not isinstance(functional_history, str):
                raise BadRequest("functional_history field is not a string")
            kwargs["functional_history"] = functional_history

        if "structure_and_function" in patch_body:
            structure_and_function = patch_body["structure_and_function"]
            if not isinstance(structure_and_function, str):
                raise BadRequest("structure_and_function field is not a string")
            kwargs["structure_and_function"] = structure_and_function

        if "activity_and_participation" in patch_body:
            activity_and_participation = patch_body["activity_and_participation"]
            if not isinstance(activity_and_participation, str):
                raise BadRequest("activity_and_participation field is not a string")
            kwargs["activity_and_participation"] = activity_and_participation

        if "physical_functional_tests_results" in patch_body:
            physical_functional_tests_results = patch_body[
                "physical_functional_tests_results"
            ]
            if not isinstance(physical_functional_tests_results, str):
                raise BadRequest(
                    "physical_functional_tests_results field is not a string"
                )
            kwargs[
                "physical_functional_tests_results"
            ] = physical_functional_tests_results

        if "complementary_exams_results" in patch_body:
            complementary_exams_results = patch_body["complementary_exams_results"]
            if not isinstance(complementary_exams_results, str):
                raise BadRequest("complementary_exams_results field is not a string")
            kwargs["complementary_exams_results"] = complementary_exams_results

        if "deficiency_diagnosis" in patch_body:
            deficiency_diagnosis = patch_body["deficiency_diagnosis"]
            if not isinstance(deficiency_diagnosis, str):
                raise BadRequest("deficiency_diagnosis field is not a string")
            kwargs["deficiency_diagnosis"] = deficiency_diagnosis

        if "activity_limitation_diagnosis" in patch_body:
            activity_limitation_diagnosis = patch_body["activity_limitation_diagnosis"]
            if not isinstance(activity_limitation_diagnosis, str):
                raise BadRequest("activity_limitation_diagnosis field is not a string")
            kwargs["activity_limitation_diagnosis"] = activity_limitation_diagnosis

        if "participation_restriction_diagnosis" in patch_body:
            participation_restriction_diagnosis = patch_body[
                "participation_restriction_diagnosis"
            ]
            if not isinstance(participation_restriction_diagnosis, str):
                raise BadRequest(
                    "participation_restriction_diagnosis field is not a string"
                )
            kwargs[
                "participation_restriction_diagnosis"
            ] = participation_restriction_diagnosis

        if "environment_factors_diagnosis" in patch_body:
            environment_factors_diagnosis = patch_body["environment_factors_diagnosis"]
            if not isinstance(environment_factors_diagnosis, str):
                raise BadRequest("environment_factors_diagnosis field is not a string")
            kwargs["environment_factors_diagnosis"] = environment_factors_diagnosis

        if "functional_objectives_diagnosis" in patch_body:
            functional_objectives_diagnosis = patch_body[
                "functional_objectives_diagnosis"
            ]
            if not isinstance(functional_objectives_diagnosis, list):
                raise BadRequest(
                    "functional_objectives_diagnosis field is not a string"
                )
            kwargs["functional_objectives_diagnosis"] = functional_objectives_diagnosis

        if "therapeutic_plan_diagnosis" in patch_body:
            therapeutic_plan_diagnosis = patch_body["therapeutic_plan_diagnosis"]
            if not isinstance(therapeutic_plan_diagnosis, list):
                raise BadRequest("therapeutic_plan_diagnosis field is not a string")
            kwargs["therapeutic_plan_diagnosis"] = therapeutic_plan_diagnosis

        if "reevaluation_dates" in patch_body:
            reevaluation_dates = patch_body["reevaluation_dates"]
            if not isinstance(reevaluation_dates, list):
                raise BadRequest("reevaluation_dates field is not a string")
            kwargs["reevaluation_dates"] = reevaluation_dates

        if "academic_assessor" in patch_body:
            academic_assessor = patch_body["academic_assessor"]
            if not isinstance(academic_assessor, str):
                raise BadRequest("academic_assessor field is not a string")
            kwargs["academic_assessor"] = academic_assessor

        if "preceptor_assessor" in patch_body:
            preceptor_assessor = patch_body["preceptor_assessor"]
            if not isinstance(preceptor_assessor, str):
                raise BadRequest("preceptor_assessor field is not a string")
            kwargs["preceptor_assessor"] = preceptor_assessor

        g.session.user.update_form(form_id=form_id, **kwargs)

        return {
            "_links": {
                "self": {
                    "href": url_for("_kineticfunctionalevaluationview", form_id=form_id)
                }
            },
            "form_id": form_id,
        }
