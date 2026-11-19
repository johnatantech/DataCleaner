import streamlit as st
import pandas as pd

st.title("Dashboard de Produtos")

dados = {
    "Produto": ["Notebook Dell", "Notebook Acer", "Notebook Lenovo"],
    "Preco": [3500, 2900, 3100]
}

df = pd.DataFrame(dados)

st.dataframe(df)

st.bar_chart(df.set_index("Produto"))