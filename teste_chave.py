#!/usr/bin/env python3

from modulos.extrair_chave import extrair_numero_nota

print()

chave = input("Digite a chave da NF-e: ")

nota = extrair_numero_nota(chave)

if nota:
    print()
    print(f"Número da nota: {nota}")
else:
    print()
    print("Chave inválida.")
