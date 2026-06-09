#!/usr/bin/env python3

import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path
from datetime import datetime
import threading
import requests
import zipfile
import os

WEBHOOK_URL = "https://discord.com/api/webhooks/1503887285324877825/Br94v7dk6qStQ8ADGIb5nlJaevG05852-VNMwGaDNtjGf7RXX10hrsgBq6tZ9WWZnFPR"


class App:

    def __init__(self, root):

        self.root = root
        self.root.title("Download de XMLs NF-e")
        self.root.geometry("800x600")

        tk.Label(
            root,
            text="CNPJ",
            font=("Arial", 10, "bold")
        ).pack(pady=5)

        self.cnpj = tk.Entry(root, width=40)
        self.cnpj.pack()

        tk.Label(
            root,
            text="Notas separadas por vírgula",
            font=("Arial", 10, "bold")
        ).pack(pady=5)

        self.notas = tk.Text(
            root,
            height=6,
            width=90
        )
        self.notas.pack()

        self.botao = tk.Button(
            root,
            text="Baixar Notas",
            command=self.iniciar_download,
            width=25,
            height=2
        )

        self.botao.pack(pady=10)

        tk.Label(
            root,
            text="Log"
        ).pack()

        self.log = scrolledtext.ScrolledText(
            root,
            height=20
        )

        self.log.pack(
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


root = tk.Tk()

app = App(root)

root.mainloop()

# teste github
