#!/usr/bin/env python3

from modulos.download_por_chave import (
    obter_numero_por_chave,
    baixar_xml_por_chave
)

cnpj = input("Digite o CNPJ: ").strip()

chave = input(
    "Digite a chave da NF-e: "
).strip()

try:

    numero = obter_numero_por_chave(
        chave
    )

    print()
    print(
        f"Número encontrado: {numero}"
    )

    xml = baixar_xml_por_chave(
        cnpj,
        chave
    )

    print()
    print(
        f"XML recebido com {len(xml)} caracteres."
    )

    print()
    print(
        "Primeiros 500 caracteres:"
    )

    print(xml[:500])

except Exception as erro:

    print()
    print(f"Erro: {erro}")