from config.fhir_systems import (
    HOSPITAL_PRACTITIONER_SYSTEM,
    EMERGENCY_PRACTITIONER_SYSTEM,
    PHARMACY_PRACTITIONER_SYSTEM,
    INPATIENT_PRACTITIONER_SYSTEM
)


def map_practitioner(
    practitioner_master_id,
    df_practitioners,
    df_practitioner_identifiers
):
    # ---------------------------------------------------------
    # 1. PROCURAR O PROFISSIONAL NA TABELA MASTER
    # ---------------------------------------------------------

    # Procuramos o profissional através do identificador
    # canónico utilizado pelo nosso modelo.
    practitioner_matches = df_practitioners[
        df_practitioners["practitioner_master_id"]
        == practitioner_master_id
    ]

    # Se não existir correspondência,
    # não conseguimos criar o recurso Practitioner.
    if len(practitioner_matches) == 0:
        return None

    # O identificador canónico deve ser único.
    # Mais do que uma linha indica um problema
    # de qualidade dos dados.
    if len(practitioner_matches) > 1:
        raise ValueError(
            f"Multiple practitioners found for "
            f"{practitioner_master_id}"
        )

    # Selecionamos a única linha encontrada.
    practitioner = practitioner_matches.iloc[0]

    # ---------------------------------------------------------
    # 2. PROCURAR OS IDENTIFICADORES LOCAIS
    # ---------------------------------------------------------

    # Um mesmo profissional pode possuir identificadores
    # diferentes nos sistemas de Urgência, Farmácia
    # ou Internamento.
    identifier_matches = df_practitioner_identifiers[
        df_practitioner_identifiers["practitioner_master_id"]
        == practitioner_master_id
    ]

    # Lista que irá conter todos os identifiers FHIR.
    identifiers = []

    # ---------------------------------------------------------
    # 3. IDENTIFICADOR CANÓNICO
    # ---------------------------------------------------------

    # Adicionamos primeiro o identificador canónico
    # utilizado pela nossa camada de interoperabilidade.
    #
    # Exemplo:
    # PRAC001
    identifiers.append({
        "system": HOSPITAL_PRACTITIONER_SYSTEM,
        "value": practitioner_master_id
    })

    # ---------------------------------------------------------
    # 4. MAPEAR SISTEMAS DE ORIGEM
    # ---------------------------------------------------------

    # Cada sistema de origem possui o seu próprio namespace.
    #
    # Em vez de construir URLs dinamicamente,
    # usamos as constantes centralizadas em
    # config/fhir_systems.py.
    source_system_mapping = {
        "EMERGENCY": EMERGENCY_PRACTITIONER_SYSTEM,
        "PHARMACY": PHARMACY_PRACTITIONER_SYSTEM,
        "INPATIENT": INPATIENT_PRACTITIONER_SYSTEM
    }

    # ---------------------------------------------------------
    # 5. ADICIONAR IDENTIFICADORES LOCAIS
    # ---------------------------------------------------------

    for _, identifier_row in identifier_matches.iterrows():

        # Sistema onde o identificador local foi atribuído.
        source_system = identifier_row["source_system"]

        # ID utilizado nesse sistema.
        source_id = identifier_row["source_id"]

        # Se aparecer um sistema que não conhecemos,
        # não devemos inventar automaticamente um namespace.
        if source_system not in source_system_mapping:
            raise ValueError(
                f"Unknown practitioner source system: "
                f"{source_system}"
            )

        # Obtemos o namespace correspondente
        # a partir da configuração central.
        identifier_system = source_system_mapping[source_system]

        # Preservamos o identificador local no recurso FHIR.
        identifiers.append({
            "system": identifier_system,
            "value": source_id
        })

    # ---------------------------------------------------------
    # 6. CONSTRUIR O RECURSO PRACTITIONER
    # ---------------------------------------------------------

    practitioner_resource = {
        "resourceType": "Practitioner",

        # O Practitioner pode ter vários identifiers:
        # um canónico + IDs locais dos sistemas.
        "identifier": identifiers,

        # Nesta V1 utilizamos apenas o nome sintético
        # do profissional como representação legível.
        "name": [
            {
                "text": practitioner["display_name"]
            }
        ]
    }

    # ---------------------------------------------------------
    # 7. DEVOLVER O RECURSO FHIR
    # ---------------------------------------------------------

    return practitioner_resource