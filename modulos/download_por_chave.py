import requests

from modulos.extrair_chave import extrair_numero_nota


def obter_numero_por_chave(chave):

    numero = extrair_numero_nota(chave)

    if not numero:
        raise ValueError(
            f"Chave inválida: {chave}"
        )

    return numero


def baixar_xml_por_chave(cnpj, chave):

    numero = obter_numero_por_chave(chave)

    url = (
        f"https://nfe.epoc.com.br/"
        f"download-nota/{cnpj}/{numero}"
    )

    resposta = requests.get(
        url,
        timeout=60
    )

    return resposta.text