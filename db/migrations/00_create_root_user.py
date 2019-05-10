import bcrypt

import utils
from db.manager import manager as dbman


if __name__ == "__main__":
    user, created = dbman.auth.create_user(
        "xxx.xxx.xxx-xx",
        bcrypt.hashpw(
            utils.env.get("database", "password").encode("utf-8"), bcrypt.gensalt()
        ),
        "FisUFBA",
    )
    if not created:
        print("User already exist!")
    else:
        print("User created successfully!")
