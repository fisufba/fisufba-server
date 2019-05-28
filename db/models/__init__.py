from db.models.base import db
from db.models.auth import _AUTH_TABLES
from db.models.forms import _FORMS_TABLES

DB_TABLES = _AUTH_TABLES + _FORMS_TABLES
