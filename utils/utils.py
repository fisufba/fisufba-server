def mask_cpf(cpf: str) -> str:
    assert len(cpf) == 11
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def unmask_cpf(cpf: str) -> str:
    assert len(cpf) == 14
    return cpf.replace(".", "").replace("-", "")
