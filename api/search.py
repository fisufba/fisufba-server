from db.models.forms import User


def search_user(**kwargs):

    # cpf and phone number are searched by their prefixes
    # display_name and email are searched by their substrings

    query = User.select().where(
        (User.cpf.startswith(kwargs.get("cpf")) if "cpf" in kwargs else True)
        & (
            User.display_name.contains(kwargs.get("display_name"))
            if "display_name" in kwargs
            else True
        )
        & (User.phone.startswith(kwargs.get("phone")) if "phone" in kwargs else True)
        & (User.email.contains(kwargs.get("email")) if "email" in kwargs else True)
    )

    return query
