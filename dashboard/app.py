"""Painel Streamlit do DataCleaner. Execute: streamlit run dashboard/app.py"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

st.set_page_config(page_title="DataCleaner Pro", page_icon="🧹", layout="wide")
st.title("🧹 DataCleaner Pro")

if not config.ARQUIVO_TRATADO.exists():
    st.warning("Nenhuma base tratada encontrada. Rode `python main.py` primeiro.")
    st.stop()

abas = pd.read_excel(config.ARQUIVO_TRATADO, sheet_name=None)
validos = abas.get(config.ABA_VALIDOS, pd.DataFrame())
invalidos = abas.get(config.ABA_INVALIDOS, pd.DataFrame())
total = len(validos) + len(invalidos)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Registros tratados", total)
c2.metric("Válidos", len(validos))
c3.metric("Inválidos", len(invalidos))
c4.metric("Taxa de validade", f"{len(validos) / total:.0%}" if total else "-")

if not invalidos.empty:
    st.subheader("Motivos de invalidez")
    motivos = invalidos["motivo"].str.split("; ").explode().value_counts()
    st.bar_chart(motivos, horizontal=True)

aba_v, aba_i = st.tabs([f"✅ Válidos ({len(validos)})", f"⚠️ Inválidos ({len(invalidos)})"])
with aba_v:
    st.dataframe(validos, width="stretch", hide_index=True)
with aba_i:
    st.dataframe(invalidos, width="stretch", hide_index=True)
