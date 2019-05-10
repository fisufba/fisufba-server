from db.models import DB
from db.models import DB_TABLES


if __name__ == "__main__":
    DB.connect()
    DB.create_tables(DB_TABLES)
