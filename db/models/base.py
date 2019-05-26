from peewee import Model, PostgresqlDatabase

import utils


db = PostgresqlDatabase(
    database=utils.env.get("database", "database"),
    user=utils.env.get("database", "role"),
    password=utils.env.get("database", "password"),
)


class _BaseModel(Model):
    class Meta:
        database = db
