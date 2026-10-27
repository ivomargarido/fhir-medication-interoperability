import json
from pathlib import Path


def save_fhir_resource(resource, output_path):
    # Converte o caminho recebido para um objeto Path.
    output_path = Path(output_path)

    # Garante que a pasta de destino existe.
    # Se não existir, é criada automaticamente.
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Abre o ficheiro em modo de escrita.
    # encoding="utf-8" evita problemas com caracteres especiais.
    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        # Converte o dicionário Python para JSON.
        #
        # indent=2 deixa o ficheiro legível.
        # ensure_ascii=False preserva caracteres UTF-8.
        json.dump(
            resource,
            file,
            indent=2,
            ensure_ascii=False
        )

    # Devolve o caminho final para facilitar testes
    # e confirmação no notebook.
    return output_path