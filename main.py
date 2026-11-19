import logging

logging.basicConfig(
    filename='logs/processamento.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

from tratamento import DataCleaner
from relatorios import gerar_relatorio

arquivo = "entrada/clientes.xlsx"

cleaner = DataCleaner()

df = cleaner.carregar_arquivo(arquivo)

df_tratado = cleaner.tratar(df)

df_tratado.to_excel(
    "saida/dados_tratados.xlsx",
    index=False
)

gerar_relatorio(
    cleaner.relatorio
)

print("Processamento concluído.")