"""App web do DataCleaner. Execute: streamlit run streamlit_app.py

Os arquivos enviados são processados em memória e não são gravados no servidor.
"""

from io import BytesIO

import altair as alt
import pandas as pd
import streamlit as st

import config
from relatorios import ROTULOS, salvar_base, tabela_relatorio
from tratamento import DataCleaner

VERDE = "#1F6F5C"
VERMELHO = "#B4432F"
ARQUIVO_EXEMPLO = config.BASE_DIR / "exemplos" / "clientes_exemplo.csv"
REPOSITORIO = "https://github.com/johnatantech/DataCleaner"

NOMES_COLUNAS = {
    "nome": "Nome", "email": "E-mail", "telefone": "Telefone", "documento": "CPF/CNPJ",
    "cpf": "CPF", "cnpj": "CNPJ", "cep": "CEP", "uf": "UF", "data_nascimento": "Nascimento",
}
COLUNAS_TABELA = {chave: st.column_config.TextColumn(rotulo) for chave, rotulo in NOMES_COLUNAS.items()}

st.set_page_config(page_title="DataCleaner", page_icon="🧹", layout="wide")


# ------------------------------------------------------------------ processamento

@st.cache_data(show_spinner=False, max_entries=20)
def processar(conteudo: bytes, nome: str, obrigatorios: tuple):
    cleaner = DataCleaner()
    df = cleaner.carregar_arquivo(BytesIO(conteudo), nome=nome)

    if len(df) > config.LIMITE_LINHAS_APP:
        raise ValueError(
            f"O arquivo tem {len(df):,} linhas. O limite da versão web é "
            f"{config.LIMITE_LINHAS_APP:,}. Para arquivos maiores, use a linha de comando."
        ).replace(",", ".")

    validos, invalidos = cleaner.tratar(df, campos_obrigatorios=list(obrigatorios))

    excel = BytesIO()
    salvar_base(validos, invalidos, excel, relatorio=cleaner.relatorio)
    return validos, invalidos, cleaner.relatorio, excel.getvalue()


# ------------------------------------------------------------------ gráficos

def grafico_triagem(n_validos, n_invalidos):
    dados = pd.DataFrame({
        "situacao": ["Válidos", "Inválidos"],
        "total": [n_validos, n_invalidos],
        "ordem": [0, 1],
    })
    total = n_validos + n_invalidos
    dados["rotulo"] = [
        f"{n} {nome.lower()} ({n / total:.0%})" if n else ""
        for n, nome in zip(dados["total"], dados["situacao"])
    ]

    base = alt.Chart(dados).encode(
        x=alt.X("total:Q", stack="normalize", axis=None),
        order="ordem:O",
    )
    barras = base.mark_bar(height=44, cornerRadius=4).encode(
        color=alt.Color(
            "situacao:N",
            scale=alt.Scale(domain=["Válidos", "Inválidos"], range=[VERDE, VERMELHO]),
            legend=None,
        ),
        tooltip=[alt.Tooltip("situacao:N", title="Situação"), alt.Tooltip("total:Q", title="Registros")],
    )
    textos = base.mark_text(color="white", fontWeight="bold", fontSize=14).encode(
        x=alt.X("pos:Q", axis=None), text="rotulo:N"
    ).transform_stack(
        stack="total", as_=["x0", "x1"], groupby=[], sort=[alt.SortField("ordem")], offset="normalize"
    ).transform_calculate(pos="(datum.x0 + datum.x1) / 2")

    return (barras + textos).properties(height=50).configure_view(stroke=None)


def grafico_motivos(invalidos):
    motivos = (
        invalidos["motivo"].str.split("; ").explode().value_counts()
        .rename_axis("motivo").reset_index(name="registros")
    )
    altura = max(120, 34 * len(motivos))
    barras = alt.Chart(motivos).mark_bar(color=VERMELHO, cornerRadiusEnd=3).encode(
        x=alt.X("registros:Q", title="Registros", axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("motivo:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
        tooltip=[alt.Tooltip("motivo:N", title="Motivo"), alt.Tooltip("registros:Q", title="Registros")],
    )
    rotulos = barras.mark_text(align="left", dx=4, color="#1E2A38").encode(text="registros:Q")
    return (barras + rotulos).properties(height=altura).configure_view(stroke=None)


# ------------------------------------------------------------------ barra lateral

with st.sidebar:
    st.subheader("Configuração")
    obrigatorios = st.multiselect(
        "Campos obrigatórios",
        options=list(config.CAMPOS_DISPONIVEIS),
        default=config.CAMPOS_OBRIGATORIOS,
        format_func=config.CAMPOS_DISPONIVEIS.get,
        help="Registros sem estes campos vão para a aba de inválidos.",
    )

    with st.expander("O que é validado"):
        st.markdown(
            "- **CPF e CNPJ** pelo dígito verificador, incluindo o CNPJ alfanumérico\n"
            "- **Telefone** com DDD existente e formato de celular ou fixo\n"
            "- **E-mail**, **CEP**, **UF** e **data de nascimento**\n"
            "- **Duplicidade** de linhas e de CPF/CNPJ\n\n"
            "Cabeçalhos como *E-mail*, *Celular*, *CPF/CNPJ* e *Data de Nascimento* "
            "são reconhecidos automaticamente."
        )

    st.caption(
        "🔒 Os arquivos são processados em memória e não ficam salvos no servidor. "
        "Mesmo assim, evite enviar dados pessoais reais em uma demonstração pública."
    )
    st.caption(f"[Código no GitHub]({REPOSITORIO})")


# ------------------------------------------------------------------ entrada

st.title("DataCleaner")
st.write(
    "Envie uma planilha de cadastros e receba os registros separados em válidos e "
    "inválidos, com o motivo de cada problema."
)

if "usar_exemplo" not in st.session_state:
    st.session_state.usar_exemplo = False

col_upload, col_exemplo = st.columns([3, 1], vertical_alignment="bottom")
with col_upload:
    upload = st.file_uploader("Planilha (.xlsx ou .csv, até 10 MB)", type=["xlsx", "csv"])
with col_exemplo:
    if st.button("Testar com dados de exemplo", width="stretch"):
        st.session_state.usar_exemplo = True
    st.download_button(
        "Baixar modelo de planilha",
        data=ARQUIVO_EXEMPLO.read_bytes(),
        file_name="modelo_clientes.csv",
        mime="text/csv",
        width="stretch",
    )

if upload is not None:
    st.session_state.usar_exemplo = False
    conteudo, nome = upload.getvalue(), upload.name
elif st.session_state.usar_exemplo:
    conteudo, nome = ARQUIVO_EXEMPLO.read_bytes(), ARQUIVO_EXEMPLO.name
    st.info("Usando o arquivo de exemplo, com dados fictícios. Envie sua planilha para substituí-lo.")
else:
    st.write("")
    passo1, passo2, passo3 = st.columns(3)
    passo1.markdown("**1. Envie a planilha**  \nColunas como nome, CPF/CNPJ, e-mail, telefone, CEP, UF e data de nascimento.")
    passo2.markdown("**2. Veja o diagnóstico**  \nQuantos registros passaram e por que os outros foram recusados.")
    passo3.markdown("**3. Baixe o Excel tratado**  \nAbas separadas de válidos e inválidos, com a linha de origem de cada problema.")
    st.stop()


# ------------------------------------------------------------------ resultado

try:
    with st.spinner("Validando registros..."):
        validos, invalidos, relatorio, excel = processar(conteudo, nome, tuple(obrigatorios))
except ValueError as erro:
    st.error(str(erro))
    st.stop()
except Exception:
    st.error("Não foi possível ler o arquivo. Confira se ele não está corrompido ou protegido por senha.")
    st.stop()

total = len(validos) + len(invalidos)
if total == 0:
    st.warning("A planilha não tem registros para validar.")
    st.stop()

st.divider()

cabecalho, botao = st.columns([3, 1], vertical_alignment="center")
with cabecalho:
    st.subheader(f"{total} registros após remover duplicados")
with botao:
    st.download_button(
        "Baixar Excel tratado",
        data=excel,
        file_name=f"{nome.rsplit('.', 1)[0]}_tratado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
        width="stretch",
    )

st.altair_chart(grafico_triagem(len(validos), len(invalidos)), width="stretch")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Registros lidos", relatorio["registros_lidos"])
m2.metric("Duplicados removidos", relatorio["duplicados_removidos"])
m3.metric("Taxa de validade", f"{len(validos) / total:.0%}")
m4.metric("Campos vazios na origem", relatorio["campos_vazios_na_origem"])

if not invalidos.empty:
    st.markdown("#### Por que os registros foram recusados")
    st.caption("Um registro pode ter mais de um motivo.")
    st.altair_chart(grafico_motivos(invalidos), width="stretch")

aba_validos, aba_invalidos, aba_relatorio = st.tabs(
    [f"Válidos ({len(validos)})", f"Inválidos ({len(invalidos)})", "Relatório"]
)
with aba_validos:
    if validos.empty:
        st.write("Nenhum registro passou em todas as validações.")
    else:
        st.dataframe(validos, hide_index=True, width="stretch", column_config=COLUNAS_TABELA)
with aba_invalidos:
    if invalidos.empty:
        st.write("Nenhum problema encontrado.")
    else:
        st.caption("A coluna Linha indica onde o registro está na planilha enviada, para corrigir na fonte.")
        st.dataframe(
            invalidos,
            hide_index=True,
            width="stretch",
            column_config={
                **COLUNAS_TABELA,
                "linha_origem": st.column_config.NumberColumn("Linha", width="small"),
                "motivo": st.column_config.TextColumn("Motivo", width="large"),
            },
        )
with aba_relatorio:
    st.dataframe(tabela_relatorio(relatorio), hide_index=True, width="stretch")
