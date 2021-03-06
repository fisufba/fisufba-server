import datetime
import secrets
from typing import Dict, List, Optional, Set, Union

import bcrypt
import peewee
from werkzeug.exceptions import BadRequest, Conflict, Forbidden, NotFound

import utils
import api.db_wrapper._forms as forms_wrapper
from db.models import auth, forms


class User:
    """Python class that abstracts or wraps the auth.User methods.

    Attributes:
        id: the User's id.
        cpf: the User's CPF.
        display_name: the User's display name.
        email: the User's email.

    """

    def __init__(self, cpf: str = None, password: str = None, _user: auth.User = None):
        """Initializes this User.

        Notes:
            It only accept two kinds of argument combination:
                0 - `cpf` is not None, `password` is not None and `_user` is None;
                1 - `cpf` is None, `password` is None and `_user` is not None.
            The latter combination is for internal purposes only.

        Args:
            cpf: the auth.User's CPF.
            password: the auth.User's password.
            _user: this User representation in the database.

        """
        if _user is None:
            assert cpf is not None
            assert password is not None

            if not utils.is_valid_cpf(cpf):
                raise BadRequest("invalid cpf")

            try:
                _user = auth.User.get(cpf=cpf)
            except auth.User.DoesNotExist:
                raise Forbidden("user does not exist")

            if not bcrypt.checkpw(
                password.encode("utf-8"), _user.password.encode("utf-8")
            ):
                raise Forbidden("wrong password")
        else:
            assert cpf is None
            assert password is None

        self._user = _user
        self.id = self._user.id
        self.cpf = self._user.cpf
        self.display_name = self._user.display_name
        self.phone = self._user.phone
        self.email = self._user.email

        self._permissions = set(
            permission.codename
            for permission in auth.Permission.select(auth.Permission.codename)
            .join(auth.GroupPermissions)
            .join(auth.Group)
            .join(auth.UserGroups)
            .switch(auth.Permission)
            .where(auth.UserGroups.user == self._user)
        )

    def create_session(self) -> str:
        """Creates an auth.Session in the database.

        Returns:
            The token of the created auth.Session.

        """
        session, session_token = None, None
        while session_token is None:
            try:
                session = auth.Session.create(
                    user=self._user, token=secrets.token_hex(64)
                )
                session_token = session.token
            except peewee.IntegrityError:
                continue

        now = datetime.datetime.utcnow()
        query = auth.User.update(last_login=now, updated_at=now).where(
            auth.User.id == self.id
        )
        if query.execute() == 0:
            auth.Session.update(expire_date=now, updated_at=now).where(
                auth.Session.token == session_token
            )
            # This is indeed an internal server error.
            raise Exception("login Failed")

        return session_token

    def create_user(
        self,
        cpf: str,
        password: str,
        display_name: str,
        phone: str,
        email: str,
        user_group_names: Set[str],
    ) -> int:
        """Creates an auth.User in the database.

        Args:
            cpf: the auth.User's CPF.
            password: the auth.User's password.
            display_name: the auth.User's display name.
            phone: the auth.User's phone.
            email: the auth.User's email.
            user_group_names: the group names to which the auth.User belongs.

        Returns:
            The id of the created auth.User.

        """
        self._validate_kwargs(
            cpf=cpf,
            password=password,
            display_name=display_name,
            phone=phone,
            email=email,
        )

        if not all(isinstance(name, str) for name in user_group_names):
            raise BadRequest("invalid group name in user_group_names")

        creation_kwargs = self._convert_kwarg_values(
            cpf=cpf,
            password=password,
            display_name=display_name,
            phone=phone,
            email=email,
        )

        user_groups = auth.Group.select().where(auth.Group.name.in_(user_group_names))
        if len(user_groups) != len(user_group_names):
            raise BadRequest("invalid user_group_names")

        required_permissions = set(
            f"create_{group_name}" for group_name in user_group_names
        )
        self._check_permissions(required_permissions)

        try:
            user = auth.User.create(**creation_kwargs)
        except peewee.IntegrityError:
            raise Conflict("user already exists")

        try:
            for group in user_groups:
                auth.UserGroups.create(user=user, group=group)
        except peewee.IntegrityError:
            auth.User.delete().where(auth.User.id == user.id)
            raise Conflict("duplicated user_group relation")

        return user.id

    def get_serialized_user(self, user_id: int) -> dict:
        """Retrieves the serialized data of an auth.User from the database.

        Args:
            user_id: the id of the target auth.User.

        Returns:
            A serialized auth.User from the database.

        """
        user_group_names = self._get_user_group_names(user_id)

        #: Own data reading is guaranteed by the system.
        if user_id != self._user.id:
            required_permissions = set(
                f"read_{group_name}_data" for group_name in user_group_names
            )
            self._check_permissions(required_permissions)

        try:
            user = auth.User.get_by_id(user_id)
        except auth.User.DoesNotExist:
            if user_id == self._user.id:
                # This is indeed an internal server error.
                raise Exception("user not found")
            raise NotFound("user not found")

        return dict(
            id=user.id,
            cpf=user.cpf,
            display_name=user.display_name,
            phone=user.phone,
            email=user.email,
            groups=list(user_group_names),
            forms=self._get_serialized_user_form_ids(user),
            last_login=None if user.last_login is None else user.last_login.isoformat(),
            verified_at=None
            if user.verified_at is None
            else user.verified_at.isoformat(),
            deactivated_at=None
            if user.deactivated_at is None
            else user.deactivated_at.isoformat(),
            updated_at=None if user.updated_at is None else user.updated_at.isoformat(),
            created_at=None if user.created_at is None else user.created_at.isoformat(),
        )

    def update_user(self, user_id: int, **kwargs):
        """Updates an auth.User in the database.

        Args:
            user_id: the id of the target auth.User.
            **kwargs: kwargs that may contain:
                cpf: the new auth.User's CPF.
                password: the new auth.User's password.
                display_name: the new auth.User's display name.
                phone: the new auth.User's phone.
                email: the new auth.User's email.

        """
        self._validate_kwargs(**kwargs)

        update_kwargs = self._convert_kwarg_values(**kwargs)

        user_group_names = self._get_user_group_names(user_id)

        required_permissions = set(
            f"change_{group_name}_data" for group_name in user_group_names
        )
        self._check_permissions(required_permissions)

        query = auth.User.update(
            **update_kwargs, updated_at=datetime.datetime.utcnow()
        ).where(auth.User.id == user_id)
        if query.execute() == 0:
            # Is this an internal server error?
            raise Exception("not updated")

        if user_id == self.id:
            self._restore()

    def create_form(
        self, form_t: forms_wrapper.FormTypes, user_id: int, **kwargs
    ) -> int:
        self._check_permissions({f"create_form"})

        if form_t is forms_wrapper.FormTypes.PatientInformation:
            form = forms_wrapper.PatientInformation()
        elif form_t is forms_wrapper.FormTypes.SociodemographicEvaluation:
            form = forms_wrapper.SociodemographicEvaluation()
        elif form_t is forms_wrapper.FormTypes.KineticFunctionalEvaluation:
            form = forms_wrapper.KineticFunctionalEvaluation()
        elif form_t is forms_wrapper.FormTypes.Goniometry:
            form = forms_wrapper.Goniometry()
        elif form_t is forms_wrapper.FormTypes.AshworthScale:
            form = forms_wrapper.AshworthScale()
        elif form_t is forms_wrapper.FormTypes.SensoryEvaluation:
            form = forms_wrapper.SensoryEvaluation()
        elif form_t is forms_wrapper.FormTypes.RespiratoryMuscleStrength:
            form = forms_wrapper.RespiratoryMuscleStrength()
        elif form_t is forms_wrapper.FormTypes.PainEvaluation:
            form = forms_wrapper.PainEvaluation()
        elif form_t is forms_wrapper.FormTypes.MuscleStrength:
            form = forms_wrapper.MuscleStrength()
        else:
            # This is indeed an internal server error.
            raise NotImplementedError("unexpected form type")

        try:
            user = auth.User.get_by_id(user_id)
        except auth.User.DoesNotExist:
            raise NotFound("user not found")

        if "patient" not in self._get_user_group_names(user.id):
            raise BadRequest("target user is not a patient")

        return form.create(user=user, **kwargs)

    def get_serialized_form(
        self, form_t: forms_wrapper.FormTypes, form_id: int
    ) -> dict:
        if form_t is forms_wrapper.FormTypes.PatientInformation:
            form = forms_wrapper.PatientInformation(form_id)
        elif form_t is forms_wrapper.FormTypes.SociodemographicEvaluation:
            form = forms_wrapper.SociodemographicEvaluation(form_id)
        elif form_t is forms_wrapper.FormTypes.KineticFunctionalEvaluation:
            form = forms_wrapper.KineticFunctionalEvaluation(form_id)
        elif form_t is forms_wrapper.FormTypes.Goniometry:
            form = forms_wrapper.Goniometry(form_id)
        elif form_t is forms_wrapper.FormTypes.AshworthScale:
            form = forms_wrapper.AshworthScale(form_id)
        elif form_t is forms_wrapper.FormTypes.SensoryEvaluation:
            form = forms_wrapper.SensoryEvaluation(form_id)
        elif form_t is forms_wrapper.FormTypes.RespiratoryMuscleStrength:
            form = forms_wrapper.RespiratoryMuscleStrength(form_id)
        elif form_t is forms_wrapper.FormTypes.PainEvaluation:
            form = forms_wrapper.PainEvaluation(form_id)
        elif form_t is forms_wrapper.FormTypes.MuscleStrength:
            form = forms_wrapper.MuscleStrength(form_id)
        else:
            # This is indeed an internal server error.
            raise NotImplementedError("unexpected form type")

        #: Own form data reading is guaranteed by the system.
        if form.get_user_id() != self._user.id:
            self._check_permissions({f"read_form_data"})

        return form.serialized()

    def update_form(self, form_t: forms_wrapper.FormTypes, form_id: int, **kwargs):
        self._check_permissions({f"change_form_data"})

        if form_t is forms_wrapper.FormTypes.PatientInformation:
            form = forms_wrapper.PatientInformation(form_id)
        elif form_t is forms_wrapper.FormTypes.SociodemographicEvaluation:
            form = forms_wrapper.SociodemographicEvaluation(form_id)
        elif form_t is forms_wrapper.FormTypes.KineticFunctionalEvaluation:
            form = forms_wrapper.KineticFunctionalEvaluation(form_id)
        elif form_t is forms_wrapper.FormTypes.Goniometry:
            form = forms_wrapper.Goniometry(form_id)
        elif form_t is forms_wrapper.FormTypes.AshworthScale:
            form = forms_wrapper.AshworthScale(form_id)
        elif form_t is forms_wrapper.FormTypes.SensoryEvaluation:
            form = forms_wrapper.SensoryEvaluation(form_id)
        elif form_t is forms_wrapper.FormTypes.RespiratoryMuscleStrength:
            form = forms_wrapper.RespiratoryMuscleStrength(form_id)
        elif form_t is forms_wrapper.FormTypes.PainEvaluation:
            form = forms_wrapper.PainEvaluation(form_id)
        elif form_t is forms_wrapper.FormTypes.MuscleStrength:
            form = forms_wrapper.MuscleStrength(form_id)
        else:
            # This is indeed an internal server error.
            raise NotImplementedError("unexpected form type")

        form.update(**kwargs)

    def serialized_patient_search(self, **kwargs):
        self._check_permissions({f"search_patient"})

        valid_search_kwargs = {"cpf", "display_name", "email", "phone"}
        for kwarg in kwargs:
            if kwarg not in valid_search_kwargs:
                raise BadRequest(f"{kwarg} is not a searchable field")

        if "cpf" in kwargs:
            if not kwargs["cpf"].isdigit():
                raise BadRequest("invalid cpf prefix")

        if "phone" in kwargs:
            if not kwargs["phone"].isdigit():
                raise BadRequest("invalid phone prefix")

        query = (
            auth.User.select()
            .join(auth.UserGroups)
            .join(auth.Group)
            .switch(auth.User)
            .where(auth.Group.name == "patient")
        )

        if "cpf" in kwargs:
            query = query.where(auth.User.cpf.startswith(kwargs["cpf"]))
        if "display_name" in kwargs:
            query = query.where(auth.User.display_name.contains(kwargs["display_name"]))
        if "phone" in kwargs:
            query = query.where(auth.User.phone.startswith(kwargs["phone"]))
        if "email" in kwargs:
            query = query.where(auth.User.email.contains(kwargs["email"]))

        return [
            {
                "id": item.id,
                "cpf": item.cpf,
                "display_name": item.display_name,
                "phone": item.phone,
                "email": item.email,
                "groups": list(self._get_user_group_names(item.id)),
            }
            for item in query.execute()
        ]

    def _check_permissions(self, required_permissions: Set[str]):
        if len(required_permissions.difference(self._permissions)) > 0:
            raise Forbidden("not enough permission")

    def _convert_kwarg_values(self, **kwargs):
        if "password" in kwargs:
            kwargs["password"] = bcrypt.hashpw(
                kwargs["password"].encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

        return kwargs

    def _get_serialized_user_form_ids(
        self, user: auth.User
    ) -> Dict[str, Union[int, Optional[List[int]]]]:
        result = dict()

        form_type_to_form_model = {
            forms_wrapper.FormTypes.PatientInformation: forms.PatientInformation,
            forms_wrapper.FormTypes.SociodemographicEvaluation: forms.SociodemographicEvaluation,
            forms_wrapper.FormTypes.KineticFunctionalEvaluation: forms.KineticFunctionalEvaluation,
            forms_wrapper.FormTypes.Goniometry: forms.StructureAndFunction,
            forms_wrapper.FormTypes.AshworthScale: forms.StructureAndFunction,
            forms_wrapper.FormTypes.SensoryEvaluation: forms.StructureAndFunction,
            forms_wrapper.FormTypes.RespiratoryMuscleStrength: forms.StructureAndFunction,
            forms_wrapper.FormTypes.PainEvaluation: forms.StructureAndFunction,
            forms_wrapper.FormTypes.MuscleStrength: forms.StructureAndFunction,
        }

        for form_type, form_model in form_type_to_form_model.items():
            try:
                query = form_model.select().where(form_model.user == user)

                if form_type in forms_wrapper.STRUCTUVEANDFUNCTIONFORMTYPES:
                    #: These types have a type to differ between them.
                    query = query.where(form_model.type == form_type)

                form_ids = list(form.id for form in query.execute())
                if len(form_ids) == 0:
                    form_ids = None
            except forms.SociodemographicEvaluation.DoesNotExist:
                form_ids = None

            if form_type is forms_wrapper.FormTypes.PatientInformation and form_ids:
                #: This type has a different return from others.
                #: When it exists it must be only one
                #: and must be returned out of a list.
                result[form_type.value] = form_ids[0]
            else:
                result[form_type.value] = form_ids

        return result

    def _get_user_group_names(self, user_id: int) -> Set[str]:
        return set(
            group.name
            for group in auth.Group.select(auth.Group.name)
            .join(auth.UserGroups)
            .join(auth.User)
            .switch(auth.Group)
            .where(auth.User.id == user_id)
        )

    def _restore(self):
        try:
            self._user = auth.User.get_by_id(self.id)
        except auth.User.DoesNotExist:
            # This is indeed an internal server error.
            raise Exception("user does not exist")

        self.cpf = self._user.cpf
        self.display_name = self._user.display_name
        self.phone = self._user.phone
        self.email = self._user.email

    def _validate_kwargs(self, **kwargs):
        valid_kwargs = {"cpf", "password", "display_name", "phone", "email"}
        for kwarg in kwargs.keys():
            if kwarg not in valid_kwargs:
                # This is indeed an internal server error.
                raise TypeError(f"{kwarg} is not a valid keyword argument")

        if "cpf" in kwargs:
            if not utils.is_valid_cpf(kwargs["cpf"]):
                raise BadRequest("invalid cpf")

        if "phone" in kwargs:
            if not kwargs["phone"].isdigit():
                raise BadRequest("invalid phone")

        if "email" in kwargs:
            if kwargs["email"] is not None and not utils.is_valid_email(
                kwargs["email"]
            ):
                raise BadRequest("invalid email")


class Session:
    """Python class that abstracts or wraps the auth.Session methods.

    Attributes:
        token: the Session's token.
        user: the Session's User.

    """

    def __init__(self, token: str):
        """Initializes this Session.

        Args:
            token: the auth.Session's token.

        """
        try:
            self._session = auth.Session.get(token=token)
        except auth.Session.DoesNotExist:
            raise Forbidden("invalid session token")

        if self._session.expire_date <= datetime.datetime.utcnow():
            #: Trying to authenticate an expired session.
            raise Forbidden("expired token")

        self.token = self._session.token
        self.user = User(_user=self._session.user)

    def __eq__(self, other):
        if not isinstance(other, Session):
            return False
        return self.token == other.token and self.user.id == other.user.id

    def expire(self):
        """Updates the expire_date of this Session representation in the database for uctnow.

        """
        now = datetime.datetime.utcnow()
        query = auth.Session.update(expire_date=now, updated_at=now).where(
            auth.Session.id == self._session.id
        )
        if query.execute() == 0:
            raise Forbidden("invalid session")
