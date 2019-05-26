import bcrypt

import utils
from db.manager import manager as dbman


def do_migration():
    admin, created = dbman.auth.create_user(
        {
            "cpf": utils.env.get("admin", "cpf").replace(".", "").replace("-", ""),
            "password": bcrypt.hashpw(
                utils.env.get("admin", "password").encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8"),
            "display_name": utils.env.get("admin", "display_name"),
            "email": utils.env.get("admin", "email"),
            "group_name": "admin",
        }
    )
    assert created


if __name__ == "__main__":
    do_migration()
