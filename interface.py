"""Interface gráfica do DataCleaner."""

import logging
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import config
from main import preparar_ambiente, processar
from relatorios import ROTULOS


class App:

    def __init__(self, janela):
        self.janela = janela
        self.arquivo = None

        janela.title("DataCleaner Pro")
        janela.geometry("620x440")
        janela.minsize(520, 400)

        quadro = ttk.Frame(janela, padding=20)
        quadro.pack(fill="both", expand=True)

        ttk.Label(quadro, text="DataCleaner Pro", font=("Arial", 16, "bold")).pack(anchor="w")
        ttk.Label(quadro, text="Limpeza e padronização de cadastros (.xlsx ou .csv)").pack(anchor="w", pady=(0, 15))

        linha = ttk.Frame(quadro)
        linha.pack(fill="x")
        ttk.Button(linha, text="Selecionar arquivo", command=self.selecionar).pack(side="left")
        self.label_arquivo = ttk.Label(linha, text="Nenhum arquivo selecionado", foreground="gray")
        self.label_arquivo.pack(side="left", padx=10)

        self.botao_processar = ttk.Button(quadro, text="Processar", command=self.executar, state="disabled")
        self.botao_processar.pack(anchor="w", pady=15)

        self.barra = ttk.Progressbar(quadro, mode="determinate", value=0)
        self.barra.pack(fill="x")

        self.resultado = tk.Text(quadro, height=10, state="disabled", relief="flat")
        self.resultado.pack(fill="both", expand=True, pady=15)

        self.botao_abrir = ttk.Button(quadro, text="Abrir pasta de saída", command=self.abrir_saida)
        self.botao_abrir.pack(anchor="w")

    def selecionar(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Planilhas", "*.xlsx *.csv"), ("Excel", "*.xlsx"), ("CSV", "*.csv")]
        )
        if caminho:
            self.arquivo = caminho
            self.label_arquivo.config(text=os.path.basename(caminho), foreground="")
            self.botao_processar.config(state="normal")

    def executar(self):
        self.botao_processar.config(state="disabled")
        self.barra.config(mode="indeterminate")
        self.barra.start(10)
        self.janela.update_idletasks()

        try:
            relatorio = processar(self.arquivo)
            linhas = [f"{ROTULOS.get(k, k)}: {v}" for k, v in relatorio.items()]
            self.mostrar("Processamento concluído\n\n" + "\n".join(linhas))
        except Exception as erro:
            logging.exception("Falha no processamento")
            messagebox.showerror("Erro", str(erro))
        finally:
            self.barra.stop()
            self.barra.config(mode="determinate", value=0)
            self.botao_processar.config(state="normal")

    def mostrar(self, texto):
        self.resultado.config(state="normal")
        self.resultado.delete("1.0", tk.END)
        self.resultado.insert(tk.END, texto)
        self.resultado.config(state="disabled")

    def abrir_saida(self):
        pasta = str(config.PASTA_SAIDA)
        if sys.platform.startswith("win"):
            os.startfile(pasta)
        elif sys.platform == "darwin":
            os.system(f'open "{pasta}"')
        else:
            os.system(f'xdg-open "{pasta}"')


if __name__ == "__main__":
    preparar_ambiente()
    raiz = tk.Tk()
    App(raiz)
    raiz.mainloop()
