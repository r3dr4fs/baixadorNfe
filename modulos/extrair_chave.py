def extrair_numero_nota(chave):

    chave = ''.join(
        c for c in chave
        if c.isdigit()
    )

    if len(chave) != 44:
        return None

    numero = chave[25:34]

    return str(int(numero))