"""Gravação da base tratada e do relatório de processamento."""

import pandas as pd
from openpyxl.styles import Font, PatternFill

import config

ROTULOS = {
    "registros_lidos": "Registros lidos",
    "duplicados_removidos": "Duplicados removidos",
    "registros_validos": "Registros válidos",
    "registros_invalidos": "Registros inválidos",
    "campos_vazios_na_origem": "Campos vazios na origem",
}


def _formatar_aba(planilha, cor_cabecalho):
    """Cabeçalho destacado, primeira linha congelada, filtro e largura automática."""
    for celula in planilha[1]:
        celula.font = Font(bold=True, color="FFFFFF")
        celula.fill = PatternFill("solid", fgColor=cor_cabecalho)
    planilha.freeze_panes = "A2"
    planilha.auto_filter.ref = planilha.dimensions
    for coluna in planilha.columns:
        largura = max(len(str(c.value)) if c.value is not None else 0 for c in coluna)
        planilha.column_dimensions[coluna[0].column_letter].width = min(largura + 3, 60)


def salvar_base(validos, invalidos, destino=config.ARQUIVO_TRATADO):
    with pd.ExcelWriter(destino, engine="openpyxl") as writer:
        validos.to_excel(writer, sheet_name=config.ABA_VALIDOS, index=False)
        invalidos.to_excel(writer, sheet_name=config.ABA_INVALIDOS, index=False)
        _formatar_aba(writer.sheets[config.ABA_VALIDOS], "2E7D32")
        _formatar_aba(writer.sheets[config.ABA_INVALIDOS], "C62828")
    return destino


def gerar_relatorio(relatorio, destino=config.ARQUIVO_RELATORIO):
    resultado = pd.DataFrame(
        [(ROTULOS.get(chave, chave), valor) for chave, valor in relatorio.items()],
        columns=["Indicador", "Valor"],
    )
    with pd.ExcelWriter(destino, engine="openpyxl") as writer:
        resultado.to_excel(writer, sheet_name="Relatório", index=False)
        _formatar_aba(writer.sheets["Relatório"], "37474F")
    return destino
