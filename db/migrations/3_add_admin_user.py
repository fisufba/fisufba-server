import bcrypt

import utils
from db.models import auth


def do_migration():
    cpf = utils.env.get("admin", "cpf")
    password = utils.env.get("admin", "password")
    display_name = utils.env.get("admin", "display_name")
    email = utils.env.get("admin", "email")

    if not isinstance(cpf, str):
        raise Exception("Invalid cpf")  # TODO InvalidCPFError.
    if not utils.is_valid_cpf(cpf):
        raise Exception("Invalid cpf")  # TODO InvalidCPFError.
    if not isinstance(password, str):
        raise Exception("Invalid password")  # TODO InvalidPasswordError.
    if not isinstance(display_name, str):
        raise Exception("Invalid display_name")  # TODO InvaliDisplayNameError.
    if email is not None and not isinstance(email, str):
        raise Exception("Invalid email")  # TODO InvalidEmailError.
    if email is not None and not utils.is_valid_email(email):
        raise Exception("Invalid email")  # TODO InvalidEmailError.

    user = auth.User.create(
        cpf=utils.unmask_cpf(cpf),
        password=bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        ),
        display_name=display_name,
        email=email,
        is_verified=None if email is None else False,
    )
    user_group = auth.Group.get(name="admin")
    auth.UserGroups.create(user=user, group=user_group)


if __name__ == "__main__":
    do_migration()
