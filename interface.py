import tkinter as tk

from tkinter import filedialog
from tkinter import ttk

arquivo_selecionado = ""

def selecionar():

    global arquivo_selecionado

    arquivo_selecionado = filedialog.askopenfilename()

    label_arquivo.config(
        text=arquivo_selecionado
    )


janela = tk.Tk()

janela.title("DataCleaner Pro")

janela.geometry("700x400")

ttk.Button(
    janela,
    text="Selecionar Arquivo",
    command=selecionar
).pack(pady=20)

label_arquivo = ttk.Label(
    janela,
    text="Nenhum arquivo"
)

label_arquivo.pack()

barra = ttk.Progressbar(
    janela,
    length=300,
    mode="determinate"
)

barra.pack(pady=20)

janela.mainloop()
