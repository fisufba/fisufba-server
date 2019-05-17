import datetime

from dateutil import relativedelta
from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField
from peewee import FixedCharField
from peewee import ForeignKeyField
from peewee import TextField

from db.models.base import _BaseModel


class User(_BaseModel):
    class Meta:
        table_name = "auth_user"

    cpf = FixedCharField(max_length=11, unique=True)
    password = FixedCharField(max_length=60)

    display_name = CharField()
    email = CharField(unique=True, default=None, null=True)

    is_active = BooleanField(default=True)
    is_verified = BooleanField(default=None, null=True)

    last_login = DateTimeField(default=None, null=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow())


class Group(_BaseModel):
    class Meta:
        table_name = "auth_group"

    name = CharField(max_length=32, unique=True)


class UserGroups(_BaseModel):
    class Meta:
        table_name = "auth_user_groups"
        indexes = ((("user", "group"), True),)

    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)


class Permission(_BaseModel):
    class Meta:
        table_name = "auth_permission"

    name = CharField(unique=True)
    codename = CharField(unique=True)
    description = TextField()


class GroupPermissions(_BaseModel):
    class Meta:
        table_name = "auth_group_permissions"
        indexes = ((("group", "permission"), True),)

    group = ForeignKeyField(Group)
    permission = ForeignKeyField(Permission)


class Session(_BaseModel):
    class Meta:
        table_name = "auth_session"

    user = ForeignKeyField(User)
    token = FixedCharField(max_length=128, unique=True)

    last_access = DateTimeField(default=datetime.datetime.utcnow())
    expire_date = DateTimeField(
        default=datetime.datetime.utcnow() + relativedelta.relativedelta(years=1)
    )
    created_at = DateTimeField(default=datetime.datetime.utcnow())


_AUTH_TABLES = (User, Group, UserGroups, Permission, GroupPermissions, Session)
