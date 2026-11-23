"""Ponto de entrada do DataCleaner (linha de comando)."""

import argparse
import logging
import sys

import config
from relatorios import ROTULOS, gerar_relatorio, salvar_base
from tratamento import DataCleaner


def preparar_ambiente():
    """Cria as pastas de trabalho e configura o log."""
    for pasta in (config.PASTA_ENTRADA, config.PASTA_SAIDA, config.PASTA_LOGS):
        pasta.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(config.ARQUIVO_LOG, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


def processar(arquivo):
    """Executa o fluxo completo e devolve o relatório."""
    cleaner = DataCleaner()
    df = cleaner.carregar_arquivo(arquivo)
    validos, invalidos = cleaner.tratar(df)

    salvar_base(validos, invalidos)
    gerar_relatorio(cleaner.relatorio)

    logging.info("Base tratada salva em %s", config.ARQUIVO_TRATADO)
    logging.info("Relatório salvo em %s", config.ARQUIVO_RELATORIO)
    return cleaner.relatorio


def main():
    parser = argparse.ArgumentParser(description="Limpeza e padronização de cadastros.")
    parser.add_argument(
        "arquivo",
        nargs="?",
        default=config.PASTA_ENTRADA / "clientes.xlsx",
        help="Planilha .xlsx ou .csv (padrão: entrada/clientes.xlsx)",
    )
    args = parser.parse_args()

    preparar_ambiente()

    try:
        relatorio = processar(args.arquivo)
    except (FileNotFoundError, ValueError) as erro:
        logging.error(erro)
        sys.exit(1)

    print("\nProcessamento concluído:")
    for chave, valor in relatorio.items():
        print(f"  {ROTULOS.get(chave, chave)}: {valor}")


if __name__ == "__main__":
    main()
