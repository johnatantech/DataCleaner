"""Configurações do DataCleaner."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PASTA_ENTRADA = BASE_DIR / "entrada"
PASTA_SAIDA = BASE_DIR / "saida"
PASTA_LOGS = BASE_DIR / "logs"

ARQUIVO_TRATADO = PASTA_SAIDA / "dados_tratados.xlsx"
ARQUIVO_RELATORIO = PASTA_SAIDA / "relatorio_processamento.xlsx"
ARQUIVO_LOG = PASTA_LOGS / "processamento.log"

EXTENSOES_SUPORTADAS = {".csv", ".xlsx"}

ABA_VALIDOS = "Válidos"
ABA_INVALIDOS = "Inválidos"

# Nomes de coluna alternativos aceitos na planilha de entrada.
# Os cabeçalhos são normalizados antes (minúsculas, sem acento, "_" no lugar
# de espaços e símbolos): "E-mail" vira "e_mail", "CPF/CNPJ" vira "cpf_cnpj".
ALIASES_COLUNAS = {
    "e_mail": "email",
    "mail": "email",
    "celular": "telefone",
    "fone": "telefone",
    "tel": "telefone",
    "whatsapp": "telefone",
    "cpf_cnpj": "documento",
    "cnpj_cpf": "documento",
    "doc": "documento",
    "data_de_nascimento": "data_nascimento",
    "nascimento": "data_nascimento",
    "dt_nascimento": "data_nascimento",
    "estado": "uf",
    "nome_completo": "nome",
    "razao_social": "nome",
}

# Registros sem estes campos vão para a aba de inválidos.
CAMPOS_OBRIGATORIOS = ["nome"]

# Valor usado para preencher campos vazios na planilha final.
VALOR_PADRAO_NULO = "Não informado"
VALORES_NULOS = {}  # padrão específico por coluna, se necessário

IDADE_MAXIMA = 120
