#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from pathlib import Path
from datetime import datetime
import threading
import requests
import zipfile
import os

from modulos.extrair_chave import extrair_numero_nota

WEBHOOK_URL = "https://discord.com/api/webhooks/1503887285324877825/Br94v7dk6qStQ8ADGIb5nlJaevG05852-VNMwGaDNtjGf7RXX10hrsgBq6tZ9WWZnFPR"


class App:

    def __init__(self, root):

        self.root = root
        self.root.title("Download de XMLs NF-e")
        self.root.geometry("800x600")

        self.notebook = ttk.Notebook(root)

        self.notebook.pack(
            fill="both",
            expand=True
        )

        self.aba_download = ttk.Frame(
            self.notebook
        )

        self.aba_inutilizacao = ttk.Frame(
            self.notebook
        )

        self.aba_chave = ttk.Frame(
            self.notebook
        )

        self.notebook.add(
            self.aba_download,
            text="Download XML"
        )

        self.notebook.add(
            self.aba_inutilizacao,
            text="Inutilização"
        )

        self.notebook.add(
            self.aba_chave,
            text="Download por Chave"
        )

        tk.Label(
            self.aba_download,
            text="CNPJ",
            font=("Arial", 10, "bold")
        ).pack(pady=5)

        self.cnpj = tk.Entry(
            self.aba_download,
            width=40
        )

        self.cnpj.pack()

        tk.Label(
            self.aba_download,
            text="Notas separadas por vírgula",
            font=("Arial", 10, "bold")
        ).pack(pady=5)

        self.notas = tk.Text(
            self.aba_download,
            height=6,
            width=90
        )

        self.notas.pack()

        self.botao = tk.Button(
            self.aba_download,
            text="Baixar Notas",
            command=self.iniciar_download,
            width=25,
            height=2
        )

        self.botao.pack(pady=10)

        tk.Label(
            self.aba_download,
            text="Log"
        ).pack()

        self.log = scrolledtext.ScrolledText(
            self.aba_download,
            height=20
        )

        self.log.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # =========================
        # ABA DOWNLOAD POR CHAVE
        # =========================

        tk.Label(
            self.aba_chave,
            text="CNPJ",
            font=("Arial", 10, "bold")
        ).pack(pady=5)

        self.cnpj_chave = tk.Entry(
            self.aba_chave,
            width=40
        )

        self.cnpj_chave.pack()

        tk.Label(
            self.aba_chave,
            text="Chave da NF-e",
            font=("Arial", 10, "bold")
        ).pack(pady=5)

        self.chave_nfe = tk.Entry(
            self.aba_chave,
            width=60
        )

        self.chave_nfe.pack()

        self.botao_chave = tk.Button(
            self.aba_chave,
            text="Baixar XML",
            command=self.baixar_por_chave,
            width=25,
            height=2
        )

        self.botao_chave.pack(pady=10)

        self.log_chave = scrolledtext.ScrolledText(
            self.aba_chave,
            height=20
        )

        self.log_chave.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )
    def escrever_log(self, texto):

        self.log.insert(
            tk.END,
            texto + "\n"
        )

        self.log.see(tk.END)

        self.root.update_idletasks()

    def iniciar_download(self):

        self.botao.config(state="disabled")

        threading.Thread(
            target=self.processar,
            daemon=True
        ).start()

    def processar(self):

        try:

            cnpj = self.cnpj.get().strip()

            if not cnpj:

                messagebox.showerror(
                    "Erro",
                    "Informe o CNPJ"
                )

                self.botao.config(state="normal")
                return

            notas_texto = self.notas.get(
                "1.0",
                tk.END
            ).strip()

            if not notas_texto:

                messagebox.showerror(
                    "Erro",
                    "Informe as notas"
                )

                self.botao.config(state="normal")
                return

            lista_notas = [
                x.strip()
                for x in notas_texto.split(",")
                if x.strip()
            ]

            self.escrever_log(
                f"Total de notas informadas: {len(lista_notas)}"
            )

            downloads = Path.home() / "Downloads"

            pasta = downloads / f"notas_{cnpj}"

            pasta.mkdir(
                parents=True,
                exist_ok=True
            )

            baixadas = 0

            for nota in lista_notas:

                self.escrever_log(
                    f"Processando nota {nota}"
                )

                url = (
                    f"https://nfe.epoc.com.br/"
                    f"download-nota/{cnpj}/{nota}"
                )

                try:

                    resposta = requests.get(
                        url,
                        timeout=60
                    )

                    if (
                        "nota não existe"
                        in resposta.text.lower()
                    ):

                        self.escrever_log(
                            f"Nota {nota} não existe."
                        )

                        continue

                    arquivo_xml = (
                        pasta /
                        f"nota_{nota}.xml"
                    )

                    with open(
                        arquivo_xml,
                        "w",
                        encoding="utf-8"
                    ) as arq:

                        arq.write(
                            resposta.text
                        )

                    baixadas += 1

                    self.escrever_log(
                        f"Nota {nota} baixada."
                    )

                except Exception as erro:

                    self.escrever_log(
                        f"Erro na nota {nota}: {erro}"
                    )

            if baixadas == 0:

                self.escrever_log(
                    "Nenhuma nota válida encontrada."
                )

                self.botao.config(
                    state="normal"
                )

                return

            self.escrever_log(
                "Criando arquivo ZIP..."
            )

            zip_file = (
                downloads /
                f"notas_{cnpj}.zip"
            )

            with zipfile.ZipFile(
                zip_file,
                "w",
                zipfile.ZIP_DEFLATED
            ) as zipf:

                for arquivo in pasta.rglob("*"):

                    zipf.write(
                        arquivo,
                        arcname=arquivo.relative_to(
                            pasta.parent
                        )
                    )

            self.escrever_log(
                f"ZIP criado: {zip_file}"
            )

            self.escrever_log(
                "Enviando para Discord..."
            )

            try:

                with open(
                    zip_file,
                    "rb"
                ) as arquivo:

                    thread_name = f"Notas Baixadas - CNPJ {cnpj}"

                    resposta = requests.post(
                        WEBHOOK_URL,
                        data={
                            "content": (
                            "📄 Notas baixadas\n"
                            f"CNPJ: {cnpj}\n"
                            f"Data: {datetime.now():%d/%m/%Y %H:%M:%S}"
                        ),
                        "thread_name": thread_name
                    },
                    files={
                        "file": (
                            zip_file.name,
                            arquivo
                        )
                    }
                )       
                self.escrever_log(
                f"Status Discord: {resposta.status_code}"
                )   

                self.escrever_log(
                f"Resposta Discord: {resposta.text}"
                )

                if resposta.status_code in (
                    200,
                    204
                ):

                    self.escrever_log(
                        "Arquivo enviado para Discord."
                    )

                else:

                    self.escrever_log(
                        f"Erro Discord: "
                        f"{resposta.status_code}"
                    )

            except Exception as erro:

                self.escrever_log(
                    f"Falha ao enviar: {erro}"
                )

            self.escrever_log(
                "Processo finalizado."
            )

        except Exception as erro:

            self.escrever_log(
                f"ERRO GERAL: {erro}"
            )

        finally:

            self.botao.config(
                state="normal"
            )


    def baixar_por_chave(self):

        cnpj = self.cnpj_chave.get().strip()

        chave = self.chave_nfe.get().strip()

        if not cnpj:

            messagebox.showerror(
                "Erro",
                "Informe o CNPJ."
            )

            return

        if not chave:

            messagebox.showerror(
                "Erro",
                "Informe a chave da NF-e."
            )

            return

        try:

            numero = extrair_numero_nota(
                chave
            )

            self.log_chave.insert(
                tk.END,
                f"Nota encontrada: {numero}\n"
            )

            url = (
                f"https://nfe.epoc.com.br/"
                f"download-nota/{cnpj}/{numero}"
            )

            self.log_chave.insert(
                tk.END,
                "Baixando XML...\n"
            )

            resposta = requests.get(
                url,
                timeout=60
            )

            if (
                "nota não existe"
                in resposta.text.lower()
            ):

                self.log_chave.insert(
                    tk.END,
                    "Nota não encontrada.\n"
                )

                self.log_chave.see(tk.END)

                return

            destino = (
                Path.home()
                / "Downloads"
                / f"nota_{numero}.xml"
            )

            with open(
                destino,
                "w",
                encoding="utf-8"
            ) as arquivo:

                arquivo.write(
                    resposta.text
                )

            self.log_chave.insert(
                tk.END,
                f"XML salvo em:\n{destino}\n\n"
            )

            self.log_chave.see(tk.END)

            messagebox.showinfo(
                "Sucesso",
                f"XML salvo em:\n{destino}"
            )

        except Exception as erro:

            self.log_chave.insert(
                tk.END,
                f"Erro: {erro}\n"
            )

            self.log_chave.see(tk.END)

root = tk.Tk()

app = App(root)

root.mainloop()


