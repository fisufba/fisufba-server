import re


def is_valid_email(email: str) -> bool:
    """Checks if a string is a valid email.

        Args:
            email: Possible email to be validated.

        Returns:
            True when `email` is a valid email, False otherwise.

    """
    email_re = re.compile(r"^[^@]+@[^@$]+$")
    return email_re.match(email) is not None


def is_valid_cpf(cpf: str, with_mask: bool = True) -> bool:
    """Checks if a string is a valid CPF.

    Args:
        cpf: Possible CPF to be validated.
        with_mask: True when the CPF contains a mask (xxx.xxx.xxx-xx).
            False otherwise (xxxxxxxxxxx).

    Returns:
        True when `cpf` is a valid CPF, False otherwise.

    """
    if with_mask:
        cpf_re = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
        if cpf_re.match(cpf) is None:
            return False

        assert len(cpf) == 14  #: This never may fail.

        cpf = cpf.replace(".", "").replace("-", "")

    code, vd = cpf[:9], cpf[9:]

    assert len(code) == 9  #: This never may fail.
    assert len(vd) == 2  #: This never may fail.

    code_sum = 0
    for i, digit in enumerate(reversed(code), 2):
        code_sum += int(digit) * i

    if 11 - (code_sum % 11) <= 9:
        first_vd = 11 - (code_sum % 11)
    else:
        first_vd = 0

    if int(vd[0]) != first_vd:
        return False

    code_sum = 0
    for i, digit in enumerate(reversed([*code, vd[0]]), 2):
        code_sum += int(digit) * i

    if 11 - (code_sum % 11) <= 9:
        second_vd = 11 - (code_sum % 11)
    else:
        second_vd = 0

    if int(vd[1]) != second_vd:
        return False

    return True
