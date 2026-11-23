import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.append(str(RAIZ))
from tratamento import DataCleaner  # noqa: E402


def _processar_exemplo():
    cleaner = DataCleaner()
    df = cleaner.carregar_arquivo(RAIZ / "exemplos" / "clientes_exemplo.csv")
    validos, invalidos = cleaner.tratar(df)
    return cleaner, validos, invalidos


def test_separa_validos_e_invalidos():
    cleaner, validos, invalidos = _processar_exemplo()
    assert cleaner.relatorio["registros_lidos"] == 11
    assert cleaner.relatorio["duplicados_removidos"] == 1
    assert len(validos) + len(invalidos) == 10
    assert "motivo" not in validos.columns
    assert list(invalidos.columns[:2]) == ["linha_origem", "motivo"]


def test_aliases_de_colunas():
    _, validos, _ = _processar_exemplo()
    for coluna in ["email", "telefone", "documento", "data_nascimento"]:
        assert coluna in validos.columns


def test_cnpj_alfanumerico_valido():
    _, validos, _ = _processar_exemplo()
    assert "12.ABC.345/01DE-35" in validos["documento"].values


def test_documento_duplicado_vai_para_invalidos():
    _, _, invalidos = _processar_exemplo()
    linha = invalidos[invalidos["nome"] == "Lucas Almeida"].iloc[0]
    assert "CPF/CNPJ duplicado" in linha["motivo"]
    assert "Data de nascimento inválida" in linha["motivo"]


def test_registro_sem_nome_e_invalido():
    _, _, invalidos = _processar_exemplo()
    assert invalidos["motivo"].str.contains("Nome ausente").any()


def test_sem_colunas_opcionais():
    cleaner = DataCleaner()
    validos, invalidos = cleaner.tratar(pd.DataFrame({"Nome": ["ana", "bia"]}))
    assert len(validos) == 2 and len(invalidos) == 0
