from db.models.base import DB
from db.manager._auth import Auth


class Manager:
    def __init__(self, database):
        self._database = database

        self.auth = Auth(database)


manager = Manager(DB)
