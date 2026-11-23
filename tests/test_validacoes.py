import math
import sys
from datetime import date
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))
import validacoes as v  # noqa: E402


@pytest.mark.parametrize("email, esperado", [
    ("joao@email.com", True),
    ("joao.silva+tag@empresa.com.br", True),
    ("joao@email", False),
    ("joao silva@email.com", False),
    ("", False),
    (None, False),
    (math.nan, False),
])
def test_validar_email(email, esperado):
    assert v.validar_email(email) is esperado


@pytest.mark.parametrize("telefone, esperado", [
    ("11987654321", "(11) 98765-4321"),
    (11987654321.0, "(11) 98765-4321"),   # como o Excel lê números
    ("(11) 98765-4321", "(11) 98765-4321"),
    ("+55 21 99876-5432", "(21) 99876-5432"),
    ("1134567890", "(11) 3456-7890"),
    ("123", "123"),
    ("", None),
    (None, None),
    (math.nan, None),
])
def test_formatar_telefone(telefone, esperado):
    assert v.formatar_telefone(telefone) == esperado


@pytest.mark.parametrize("telefone, esperado", [
    ("11987654321", True),     # celular
    ("1134567890", True),      # fixo
    ("+55 21 99876-5432", True),
    ("11887654321", False),    # celular sem o 9
    ("1194567890", False),     # fixo não começa com 9
    ("20987654321", False),    # DDD inexistente
    ("123", False),
    (None, False),
])
def test_validar_telefone(telefone, esperado):
    assert v.validar_telefone(telefone) is esperado


@pytest.mark.parametrize("nome, esperado", [
    ("  joão DA silva ", "João da Silva"),
    ("MARIA   OLIVEIRA", "Maria Oliveira"),
    ("ana", "Ana"),
    ("", None),
    (None, None),
    (math.nan, None),
])
def test_padronizar_nome(nome, esperado):
    assert v.padronizar_nome(nome) == esperado


@pytest.mark.parametrize("cpf, esperado", [
    ("526.018.159-06", True),
    ("52601815906", True),
    ("8301661305", True),        # zero à esquerda perdido no Excel
    (8301661305.0, True),
    ("123.456.789-00", False),
    ("111.111.111-11", False),   # dígitos repetidos
    ("1234", False),
    (None, False),
])
def test_validar_cpf(cpf, esperado):
    assert v.validar_cpf(cpf) is esperado


def test_formatar_cpf():
    assert v.formatar_cpf("8301661305") == "083.016.613-05"


@pytest.mark.parametrize("cnpj, esperado", [
    ("93.786.579/0001-40", True),
    ("93786579000140", True),
    ("12.ABC.345/01DE-35", True),   # exemplo oficial da Receita Federal
    ("12abc34501de35", True),
    ("00.000.000/E08G-12", True),   # primeiro CNPJ alfanumérico emitido
    ("93.786.579/0001-41", False),
    ("12.ABC.345/01DE-3A", False),  # dígito verificador não pode ter letra
    ("11.111.111/1111-11", False),
    (None, False),
])
def test_validar_cnpj(cnpj, esperado):
    assert v.validar_cnpj(cnpj) is esperado


def test_formatar_cnpj():
    assert v.formatar_cnpj("12abc34501de35") == "12.ABC.345/01DE-35"


@pytest.mark.parametrize("documento, esperado", [
    ("52601815906", "526.018.159-06"),
    ("93786579000140", "93.786.579/0001-40"),
])
def test_formatar_documento(documento, esperado):
    assert v.validar_documento(documento)
    assert v.formatar_documento(documento) == esperado


@pytest.mark.parametrize("cep, esperado", [
    ("01310-100", True),
    ("1310100", True),      # zero à esquerda perdido no Excel
    ("00000000", False),
    ("9999", False),
    (None, False),
])
def test_validar_cep(cep, esperado):
    assert v.validar_cep(cep) is esperado


def test_formatar_cep():
    assert v.formatar_cep("1310100") == "01310-100"


@pytest.mark.parametrize("uf, esperado", [("SP", True), ("sp", True), (" RJ ", True), ("XX", False), (None, False)])
def test_validar_uf(uf, esperado):
    assert v.validar_uf(uf) is esperado


HOJE = date(2026, 11, 23)


@pytest.mark.parametrize("data, esperado", [
    ("15/03/1990", True),
    ("1990-03-15", True),
    ("1990-03-15 00:00:00", True),   # como o pandas lê datas do Excel em texto
    ("31/02/2000", False),           # data inexistente
    ("20/08/2030", False),           # futura
    ("01/01/1890", False),           # acima da idade máxima
    ("ontem", False),
    (None, False),
])
def test_validar_data_nascimento(data, esperado):
    assert v.validar_data_nascimento(data, hoje=HOJE) is esperado


def test_normalizar_cabecalho():
    assert v.normalizar_cabecalho(" Data de Nascimento ") == "data_de_nascimento"
    assert v.normalizar_cabecalho("CPF/CNPJ") == "cpf_cnpj"
    assert v.normalizar_cabecalho("E-mail") == "e_mail"
