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
        }
    )
    assert created
    admin_group = dbman.auth.get_group("admin")
    assert admin_group is not None
    dbman.auth.add_user_to_group(admin, admin_group)


if __name__ == "__main__":
    do_migration()
