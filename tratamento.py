import pandas as pd

from validacoes import (
    validar_email,
    formatar_telefone,
    padronizar_nome
)

class DataCleaner:

    def __init__(self):
        self.relatorio = {}

    def carregar_arquivo(self, arquivo):

        if arquivo.endswith(".csv"):
            return pd.read_csv(arquivo)

        elif arquivo.endswith(".xlsx"):
            return pd.read_excel(arquivo)

        raise Exception("Formato não suportado")

    def tratar(self, df):

        registros_iniciais = len(df)

        duplicados = df.duplicated().sum()

        df = df.drop_duplicates()

        df.columns = [
            col.strip().lower()
            for col in df.columns
        ]

        correcoes = 0

        if "nome" in df.columns:

            df["nome"] = df["nome"].apply(
                padronizar_nome
            )

        if "telefone" in df.columns:

            df["telefone"] = df["telefone"].apply(
                formatar_telefone
            )

        if "email" in df.columns:

            df["email"] = (
                df["email"]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            df["status_email"] = df[
                "email"
            ].apply(
                lambda x:
                "Valido"
                if validar_email(x)
                else "Invalido"
            )

        emails_invalidos = len(
            df[df["status_email"] == "Invalido"]
        )

        for coluna in df.columns:

            quantidade = df[coluna].isnull().sum()

            correcoes += quantidade

            df[coluna] = df[coluna].fillna(
                "Não Informado"
            )

        self.relatorio = {
            "registros_lidos": registros_iniciais,
            "duplicados": duplicados,
            "registros_finais": len(df),
            "emails_invalidos": emails_invalidos,
            "campos_corrigidos": correcoes
        }

        return df