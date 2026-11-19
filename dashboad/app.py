import streamlit as st
import pandas as pd

st.title("DataCleaner Pro Analytics")

df = pd.read_excel(
    "../saida/dados_tratados.xlsx"
)

st.dataframe(df)

st.subheader(
    "Distribuição de Emails"
)

st.bar_chart(
    df["status_email"].value_counts()
)