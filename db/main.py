from db.models import db
from db.models import DB_TABLES


if __name__ == "__main__":
    db.connect()
    db.create_tables(DB_TABLES)
