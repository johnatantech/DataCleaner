import pandas as pd


def gerar_relatorio(relatorio):

    resultado = pd.DataFrame(
        relatorio.items(),
        columns=[
            "Indicador",
            "Valor"
        ]
    )

    resultado.to_excel(
        "saida/relatorio_processamento.xlsx",
        index=False
    )

    