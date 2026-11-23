"""Classe principal de limpeza e validação de dados."""

import logging
from pathlib import Path

import pandas as pd

import config
import validacoes as v

logger = logging.getLogger(__name__)

# coluna: (função que valida, função que formata, motivo exibido quando inválido)
REGRAS = {
    "email": (v.validar_email, v.formatar_email, "E-mail inválido"),
    "telefone": (v.validar_telefone, v.formatar_telefone, "Telefone inválido"),
    "cpf": (v.validar_cpf, v.formatar_cpf, "CPF inválido"),
    "cnpj": (v.validar_cnpj, v.formatar_cnpj, "CNPJ inválido"),
    "documento": (v.validar_documento, v.formatar_documento, "CPF/CNPJ inválido"),
    "cep": (v.validar_cep, v.formatar_cep, "CEP inválido"),
    "uf": (v.validar_uf, v.formatar_uf, "UF inválida"),
    "data_nascimento": (
        lambda x: v.validar_data_nascimento(x, config.IDADE_MAXIMA),
        v.formatar_data,
        "Data de nascimento inválida",
    ),
}

COLUNAS_DOCUMENTO = {"cpf": "CPF", "cnpj": "CNPJ", "documento": "CPF/CNPJ"}


class DataCleaner:

    def __init__(self):
        self.relatorio = {}

    # ------------------------------------------------------------ leitura

    def carregar_arquivo(self, arquivo):
        caminho = Path(arquivo)

        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

        extensao = caminho.suffix.lower()
        if extensao not in config.EXTENSOES_SUPORTADAS:
            raise ValueError(
                f"Formato não suportado: {extensao}. "
                f"Use {', '.join(sorted(config.EXTENSOES_SUPORTADAS))}."
            )

        # Tudo como texto: evita perda de zeros em CPF, CEP e telefone
        if extensao == ".csv":
            df = pd.read_csv(caminho, dtype=str, encoding="utf-8-sig", sep=None, engine="python")
        else:
            df = pd.read_excel(caminho, dtype=str)

        logger.info("Arquivo carregado: %s (%d linhas)", caminho.name, len(df))
        return df

    # ------------------------------------------------------------ tratamento

    def tratar(self, df):
        """Retorna (validos, invalidos)."""
        df = self._padronizar_colunas(df.copy())
        registros_iniciais = len(df)

        df = df.replace(r"^\s*$", pd.NA, regex=True)
        nulos_originais = int(df.isna().sum().sum())

        # Linha correspondente na planilha original (cabeçalho é a linha 1)
        df.insert(0, "linha_origem", range(2, len(df) + 2))
        motivos = pd.Series([[] for _ in range(len(df))], index=df.index)

        if "nome" in df.columns:
            df["nome"] = df["nome"].apply(v.padronizar_nome)

        for coluna, (validar, formatar, motivo) in REGRAS.items():
            if coluna not in df.columns:
                continue
            for idx, valor in df[coluna].items():
                if v.vazio(valor):
                    continue
                if validar(valor):
                    df.at[idx, coluna] = formatar(valor)
                else:
                    df.at[idx, coluna] = str(valor).strip()
                    motivos[idx].append(motivo)

        for coluna in config.CAMPOS_OBRIGATORIOS:
            if coluna not in df.columns:
                logger.warning("Coluna obrigatória '%s' não encontrada.", coluna)
                continue
            for idx in df.index[df[coluna].isna()]:
                motivos[idx].append(f"{coluna.capitalize()} ausente")

        # Duplicados removidos DEPOIS da padronização
        colunas_dados = [c for c in df.columns if c != "linha_origem"]
        repetidos = df.duplicated(subset=colunas_dados)
        duplicados = int(repetidos.sum())
        df, motivos = df[~repetidos], motivos[~repetidos]

        # Mesmo documento em registros diferentes: mantém o primeiro
        for coluna, rotulo in COLUNAS_DOCUMENTO.items():
            if coluna not in df.columns:
                continue
            invalido = REGRAS[coluna][2]
            validos_doc = df[coluna].notna() & motivos.apply(lambda m: invalido not in m)
            repetido = df[coluna].where(validos_doc).duplicated() & validos_doc
            for idx in df.index[repetido]:
                motivos[idx].append(f"{rotulo} duplicado")

        df["motivo"] = motivos.apply("; ".join)
        eh_invalido = df["motivo"] != ""

        validos = df[~eh_invalido].drop(columns=["motivo", "linha_origem"])
        invalidos = df[eh_invalido]
        invalidos = invalidos[["linha_origem", "motivo"] + colunas_dados]

        validos = self._preencher_vazios(validos).reset_index(drop=True)
        invalidos = self._preencher_vazios(invalidos).reset_index(drop=True)

        self.relatorio = {
            "registros_lidos": registros_iniciais,
            "duplicados_removidos": duplicados,
            "registros_validos": len(validos),
            "registros_invalidos": len(invalidos),
            "campos_vazios_na_origem": nulos_originais,
        }
        contagem = pd.Series([m for lista in motivos for m in lista]).value_counts()
        for motivo, total in contagem.items():
            self.relatorio[motivo] = int(total)

        logger.info("Tratamento concluído: %s", self.relatorio)
        return validos, invalidos

    # ------------------------------------------------------------ auxiliares

    @staticmethod
    def _padronizar_colunas(df):
        normalizadas = [v.normalizar_cabecalho(c) for c in df.columns]
        novas = []
        for nome in normalizadas:
            alvo = config.ALIASES_COLUNAS.get(nome, nome)
            # Mantém o nome original se a coluna padrão já existir (ex.: "telefone" e "celular")
            if alvo != nome and (alvo in normalizadas or alvo in novas):
                alvo = nome
            novas.append(alvo)
        df.columns = novas
        return df

    @staticmethod
    def _preencher_vazios(df):
        df = df.copy()
        for coluna in df.columns:
            padrao = config.VALORES_NULOS.get(coluna, config.VALOR_PADRAO_NULO)
            df[coluna] = df[coluna].astype(object).where(df[coluna].notna(), padrao)
        return df
