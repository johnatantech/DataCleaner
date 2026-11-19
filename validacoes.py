import re

def validar_email(email):

    if not isinstance(email, str):
        return False

    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    return bool(re.match(padrao, email))


def formatar_telefone(telefone):

    telefone = re.sub(r'\D', '', str(telefone))

    if len(telefone) == 11:
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"

    return telefone

    
def padronizar_nome(nome):

    if not isinstance(nome, str):
        return ""

    return nome.strip().title()