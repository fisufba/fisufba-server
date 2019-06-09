import datetime
import secrets
from typing import Set

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
                raise BadRequest("Invalid cpf")

            try:
                _user = auth.User.get(cpf=cpf)
            except auth.User.DoesNotExist:
                raise Forbidden("User does not exist")

            if not bcrypt.checkpw(
                password.encode("utf-8"), _user.password.encode("utf-8")
            ):
                raise Forbidden("Password is wrong")
        else:
            assert cpf is None
            assert password is None

        self._user = _user
        self.id = self._user.id
        self.cpf = self._user.cpf
        self.display_name = self._user.display_name
        self.phone = self._user.phone
        self.email = self._user.email

        self._group_names = set(
            group.name
            for group in auth.Group.select(auth.Group.name)
            .join(auth.UserGroups)
            .switch(auth.Group)
            .where(auth.UserGroups.user == self._user)
        )

        self._permissions = set(
            permission.codename
            for permission in auth.Permission.select(auth.Permission.codename)
            .join(auth.GroupPermissions)
            .join(auth.Group)
            .switch(auth.Permission)
            .where(auth.Group.name.in_(self._group_names))
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
            raise Exception("Login Failed")

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

        creation_kwargs = self._convert_kwarg_values(
            cpf=cpf,
            password=password,
            display_name=display_name,
            phone=phone,
            email=email,
        )

        user_groups = auth.Group.select().where(auth.Group.name.in_(user_group_names))
        if len(user_groups) != len(user_group_names):
            raise BadRequest("Invalid group_names")

        required_permissions = set(
            f"create_{group_name}" for group_name in user_group_names
        )
        self._check_permissions(required_permissions)

        try:
            user = auth.User.create(**creation_kwargs)
        except peewee.IntegrityError:
            raise Conflict("User already exists")

        try:
            for group in user_groups:
                auth.UserGroups.create(user=user, group=group)
        except peewee.IntegrityError:
            auth.User.delete().where(auth.User.id == user.id)
            raise Conflict("Duplicated user_group relation")

        return user.id

    def get_serialized_user(self, user_id: int) -> dict:
        """Retrieves the serialized data of an auth.User from the database.

        Args:
            user_id: the id of the target auth.User.

        Returns:
            A serialized auth.User from the database.

        """
        user_group_names = set(
            group.name
            for group in auth.Group.select(auth.Group.name)
            .join(auth.UserGroups)
            .join(auth.User)
            .switch(auth.Group)
            .where(auth.User.id == user_id)
        )

        required_permissions = set(
            f"read_{group_name}_data" for group_name in user_group_names
        )
        self._check_permissions(required_permissions)

        try:
            user = auth.User.get_by_id(user_id)
        except auth.User.DoesNotExist:
            raise NotFound("User not found")

        return dict(
            id=user.id,
            cpf=user.cpf,
            display_name=user.display_name,
            phone=user.phone,
            email=user.email,
            groups=list(user_group_names),
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

        user_group_names = set(
            group.name
            for group in auth.Group.select(auth.Group.name)
            .join(auth.UserGroups)
            .join(auth.User)
            .switch(auth.Group)
            .where(auth.User.id == user_id)
        )

        required_permissions = set(
            f"change_{group_name}_data" for group_name in user_group_names
        )
        self._check_permissions(required_permissions)

        query = auth.User.update(
            **update_kwargs, updated_at=datetime.datetime.utcnow()
        ).where(auth.User.id == user_id)
        if query.execute() == 0:
            # Is this an internal server error?
            raise Exception("Not updated")

        if user_id == self.id:
            self._restore()

    def create_patient_information(self, user_id: int, **kwargs) -> int:
        self._check_permissions({"create_patient_information"})

        patient_information = forms_wrapper.PatientInformation()

        try:
            user = auth.User.get_by_id(user_id)
        except auth.User.DoesNotExist:
            raise NotFound("User not found")

        return patient_information.create(user=user, **kwargs)

    def get_serialized_patient_information(self, patient_information_id: int) -> dict:
        self._check_permissions({"read_patient_information_data"})

        patient_information = forms_wrapper.PatientInformation(patient_information_id)

        return patient_information.serialized()

    def update_patient_information(self, patient_information_id: int, **kwargs):
        self._check_permissions({"change_patient_information_data"})

        patient_information = forms_wrapper.PatientInformation(patient_information_id)

        patient_information.update(**kwargs)

    def create_form(
        self, patient_information_id: int, form_t: forms_wrapper.FormTypes, **kwargs
    ) -> int:
        self._check_permissions({f"create_{form_t.value}_form"})

        if form_t is forms_wrapper.FormTypes.SociodemographicEvaluation:
            form = forms_wrapper.SociodemographicEvaluation()
        elif form_t is forms_wrapper.FormTypes.KineticFunctionalEvaluation:
            form = forms_wrapper.KineticFunctionalEvaluation()
        else:
            # This is indeed an internal server error.
            raise NotImplementedError("Unexpected form type")

        try:
            patient_information = forms.PatientInformation.get_by_id(
                patient_information_id
            )
        except forms.PatientInformation.DoesNotExist:
            raise NotFound("User not found")

        return form.create(patient_information=patient_information, **kwargs)

    def get_serialized_form(
        self, form_t: forms_wrapper.FormTypes, form_id: int
    ) -> dict:
        self._check_permissions({f"read_{form_t.value}_form_data"})

        if form_t is forms_wrapper.FormTypes.SociodemographicEvaluation:
            form = forms_wrapper.SociodemographicEvaluation(form_id)
        elif form_t is forms_wrapper.FormTypes.KineticFunctionalEvaluation:
            form = forms_wrapper.KineticFunctionalEvaluation(form_id)
        else:
            # This is indeed an internal server error.
            raise NotImplementedError("Unexpected form type")

        return form.serialized()

    def update_form(self, form_t: forms_wrapper.FormTypes, form_id: int, **kwargs):
        self._check_permissions({f"change_{form_t.value}_form_data"})

        if form_t is forms_wrapper.FormTypes.SociodemographicEvaluation:
            form = forms_wrapper.SociodemographicEvaluation(form_id)
        elif form_t is forms_wrapper.FormTypes.KineticFunctionalEvaluation:
            form = forms_wrapper.KineticFunctionalEvaluation(form_id)
        else:
            # This is indeed an internal server error.
            raise NotImplementedError("Unexpected form type")

        form.update(**kwargs)

    def _check_permissions(self, required_permissions: Set[str]):
        if len(required_permissions.difference(self._permissions)) > 0:
            raise Forbidden("Not enough permission")

    def _convert_kwarg_values(self, **kwargs):
        if "cpf" in kwargs:
            kwargs["cpf"] = kwargs["cpf"]

        if "password" in kwargs:
            kwargs["password"] = bcrypt.hashpw(
                kwargs["password"].encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

        return kwargs

    def _restore(self):
        try:
            self._user = auth.User.get_by_id(self.id)
        except auth.User.DoesNotExist:
            # This is indeed an internal server error.
            raise Exception("User does not exist")

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
            raise Forbidden("Invalid session token")

        if self._session.expire_date <= datetime.datetime.utcnow():
            #: Trying to authenticate an expired session.
            raise Forbidden("Expired token")

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
            raise Forbidden("Invalid session")
