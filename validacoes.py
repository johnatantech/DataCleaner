"""Regras de padronização e validação. Funções puras, sem dependência de Pandas."""

import math
import re
import unicodedata
from datetime import date, datetime

PADRAO_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)*\.[a-zA-Z]{2,}$")

UFS = {
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
}

# DDDs em uso no Brasil (Anatel)
DDDS = {
    11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 24, 27, 28, 31, 32, 33, 34, 35, 37, 38,
    41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 53, 54, 55, 61, 62, 63, 64, 65, 66, 67, 68,
    69, 71, 73, 74, 75, 77, 79, 81, 82, 83, 84, 85, 86, 87, 88, 89, 91, 92, 93, 94, 95,
    96, 97, 98, 99,
}


# ---------------------------------------------------------------- utilitários

def vazio(valor):
    """True para None, NaN ou texto em branco."""
    if valor is None:
        return True
    if isinstance(valor, float) and math.isnan(valor):
        return True
    try:
        if valor != valor:  # pd.NA, NaT
            return True
    except TypeError:
        return True
    return isinstance(valor, str) and not valor.strip()


def _texto(valor):
    """Converte para texto. 11987654321.0 (como o Excel lê números) vira '11987654321'."""
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    return str(valor).strip()


def _digitos(valor):
    return re.sub(r"\D", "", _texto(valor))


def normalizar_cabecalho(nome):
    """'Data de Nascimento' -> 'data_de_nascimento'; 'E-mail' -> 'e_mail'."""
    sem_acento = unicodedata.normalize("NFKD", str(nome)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_")


# ---------------------------------------------------------------- nome

def padronizar_nome(nome):
    """Remove espaços extras e aplica iniciais maiúsculas. Retorna None se vazio."""
    if vazio(nome) or not isinstance(nome, str):
        return None

    preposicoes = {"da", "de", "do", "das", "dos", "e"}
    return " ".join(
        p.lower() if i > 0 and p.lower() in preposicoes else p.capitalize()
        for i, p in enumerate(nome.split())
    )


# ---------------------------------------------------------------- e-mail

def validar_email(email):
    if vazio(email) or not isinstance(email, str):
        return False
    return bool(PADRAO_EMAIL.match(email.strip()))


def formatar_email(email):
    return email.strip().lower()


# ---------------------------------------------------------------- telefone

def _digitos_telefone(telefone):
    digitos = _digitos(telefone)
    if len(digitos) in (12, 13) and digitos.startswith("55"):
        digitos = digitos[2:]
    return digitos


def validar_telefone(telefone):
    """Celular: DDD + 9 + 8 dígitos. Fixo: DDD + [2-5] + 7 dígitos."""
    if vazio(telefone):
        return False
    d = _digitos_telefone(telefone)
    if len(d) not in (10, 11) or int(d[:2]) not in DDDS:
        return False
    if len(d) == 11:
        return d[2] == "9"
    return d[2] in "2345"


def formatar_telefone(telefone):
    """Formata telefones brasileiros com DDD. Retorna None se vazio."""
    if vazio(telefone):
        return None
    d = _digitos_telefone(telefone)
    if len(d) == 11:
        return f"({d[:2]}) {d[2:7]}-{d[7:]}"
    if len(d) == 10:
        return f"({d[:2]}) {d[2:6]}-{d[6:]}"
    return d or None


# ---------------------------------------------------------------- CPF

def limpar_cpf(cpf):
    d = _digitos(cpf)
    # CPF salvo como número no Excel perde zeros à esquerda (012... vira 12...)
    if 9 <= len(d) < 11:
        d = d.zfill(11)
    return d


def validar_cpf(cpf):
    if vazio(cpf):
        return False
    d = limpar_cpf(cpf)
    if len(d) != 11 or len(set(d)) == 1:
        return False

    for tamanho in (9, 10):
        soma = sum(int(d[i]) * (tamanho + 1 - i) for i in range(tamanho))
        digito = (soma * 10) % 11 % 10
        if digito != int(d[tamanho]):
            return False
    return True


def formatar_cpf(cpf):
    d = limpar_cpf(cpf)
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"


# ---------------------------------------------------------------- CNPJ (numérico e alfanumérico)

def limpar_cnpj(cnpj):
    s = re.sub(r"[^0-9A-Za-z]", "", _texto(cnpj)).upper()
    if s.isdigit() and 12 <= len(s) < 14:
        s = s.zfill(14)
    return s


def _dv_cnpj(base):
    """Módulo 11 com valor ASCII - 48, conforme a Receita Federal (vale para letras e números)."""
    pesos = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2][-len(base):]
    soma = sum((ord(c) - 48) * p for c, p in zip(base, pesos))
    resto = soma % 11
    return "0" if resto < 2 else str(11 - resto)


def validar_cnpj(cnpj):
    """Aceita o formato numérico e o alfanumérico (em vigor desde julho de 2026)."""
    if vazio(cnpj):
        return False
    s = limpar_cnpj(cnpj)
    if not re.fullmatch(r"[0-9A-Z]{12}[0-9]{2}", s) or len(set(s)) == 1:
        return False
    dv1 = _dv_cnpj(s[:12])
    dv2 = _dv_cnpj(s[:12] + dv1)
    return s[12:] == dv1 + dv2


def formatar_cnpj(cnpj):
    s = limpar_cnpj(cnpj)
    return f"{s[:2]}.{s[2:5]}.{s[5:8]}/{s[8:12]}-{s[12:]}"


# ---------------------------------------------------------------- documento (CPF ou CNPJ)

def validar_documento(documento):
    return validar_cpf(documento) or validar_cnpj(documento)


def formatar_documento(documento):
    return formatar_cpf(documento) if validar_cpf(documento) else formatar_cnpj(documento)


# ---------------------------------------------------------------- CEP

def limpar_cep(cep):
    d = _digitos(cep)
    # CEPs de SP começam com 0 e perdem esse zero quando salvos como número
    if len(d) == 7:
        d = d.zfill(8)
    return d


def validar_cep(cep):
    if vazio(cep):
        return False
    d = limpar_cep(cep)
    return len(d) == 8 and d != "00000000"


def formatar_cep(cep):
    d = limpar_cep(cep)
    return f"{d[:5]}-{d[5:]}"


# ---------------------------------------------------------------- UF

def validar_uf(uf):
    return not vazio(uf) and _texto(uf).upper() in UFS


def formatar_uf(uf):
    return _texto(uf).upper()


# ---------------------------------------------------------------- data de nascimento

FORMATOS_DATA = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d.%m.%Y")


def converter_data(valor):
    """Retorna date ou None. Aceita texto em vários formatos e objetos de data."""
    if vazio(valor):
        return None
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    texto = _texto(valor)
    for formato in FORMATOS_DATA:
        try:
            return datetime.strptime(texto, formato).date()
        except ValueError:
            continue
    return None


def validar_data_nascimento(valor, idade_maxima=120, hoje=None):
    data = converter_data(valor)
    if data is None:
        return False
    hoje = hoje or date.today()
    idade = hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))
    return data <= hoje and idade <= idade_maxima


def formatar_data(valor):
    return converter_data(valor).strftime("%d/%m/%Y")
