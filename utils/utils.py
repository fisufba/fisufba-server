import re


def is_valid_email(email: str) -> bool:
    """Checks if a string is a valid email.

        Args:
            email: Possible email to be validated.

        Returns:
            True when `email` is a valid email, False otherwise.

    """

    email_re = re.compile(r"^[^@]+@[^@$]+$")
    if email_re.match(email) is None:
        return False
    return True


def is_valid_cpf(cpf: str) -> bool:
    """Checks if a string is a valid CPF.

    Args:
        cpf: Possible CPF to be validated.

    Returns:
        True when `cpf` is a valid CPF, False otherwise.

    """
    cpf_re = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
    if cpf_re.match(cpf) is None:
        return False

    assert len(cpf) == 14  #: This never may fail.

    code, dv = cpf.replace(".", "").split("-")

    assert len(code) == 9  #: This never may fail.
    assert len(dv) == 2  #: This never may fail.

    code_sum = 0
    for i, digit in enumerate(reversed(code), 2):
        code_sum += int(digit) * i

    if 11 - (code_sum % 11) <= 9:
        first_dv = 11 - (code_sum % 11)
    else:
        first_dv = 0

    if int(dv[0]) != first_dv:
        return False

    code_sum = 0
    for i, digit in enumerate(reversed([*code, dv[0]]), 2):
        code_sum += int(digit) * i

    if 11 - (code_sum % 11) <= 9:
        second_dv = 11 - (code_sum % 11)
    else:
        second_dv = 0

    if int(dv[1]) != second_dv:
        return False

    return True
