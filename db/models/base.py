import datetime

from peewee import Model
from peewee import PostgresqlDatabase
from peewee import DateTimeField

import utils


db = PostgresqlDatabase(
    database=utils.env.get("database", "database"),
    user=utils.env.get("database", "role"),
    password=utils.env.get("database", "password"),
    host=utils.env.get("database", "host"),
    port=utils.env.get("database", "port"),
)


class _BaseModel(Model):
    class Meta:
        database = db

    updated_at = DateTimeField(default=None, null=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow())
