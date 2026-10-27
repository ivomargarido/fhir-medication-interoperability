from src.validators.administration_validator import (
    validate_prescription_exists
)

from src.validators.medication_validator import (
    validate_medication_code_exists
)

from src.validators.timing_validator import (
    validate_administration_after_prescription
)


def validate_emergency_administrations(
    df_administrations,
    df_prescriptions,
    df_medication_mapping
):
    # Executamos cada regra de validação separadamente.
    #
    # Cada função devolve uma lista de resultados com:
    # record_id, validation_status e error_code.
    prescription_results = validate_prescription_exists(
        df_administrations,
        df_prescriptions
    )

    medication_results = validate_medication_code_exists(
        df_administrations,
        df_medication_mapping
    )

    timing_results = validate_administration_after_prescription(
        df_administrations,
        df_prescriptions
    )

    # Vamos guardar aqui o resultado consolidado
    # de cada administração.
    consolidated_results = []

    # Percorremos as administrações originais.
    for _, row in df_administrations.iterrows():

        # Identificador da administração que estamos a avaliar.
        record_id = row["er_administration_id"]

        # Lista onde guardaremos todos os erros encontrados
        # para esta administração.
        errors = []

        # Procuramos o resultado desta administração
        # na validação da prescrição.
        prescription_result = next(
            result
            for result in prescription_results
            if result["record_id"] == record_id
        )

        # Se esta regra falhou, guardamos o código do erro.
        if prescription_result["validation_status"] == "REJECTED":
            errors.append(
                prescription_result["error_code"]
            )

        # Procuramos o resultado da validação
        # do código do medicamento.
        medication_result = next(
            result
            for result in medication_results
            if result["record_id"] == record_id
        )

        # Se falhou, adicionamos também este erro.
        if medication_result["validation_status"] == "REJECTED":
            errors.append(
                medication_result["error_code"]
            )

        # Procuramos o resultado da validação temporal.
        timing_result = next(
            result
            for result in timing_results
            if result["record_id"] == record_id
        )

        # Só adicionamos erro temporal quando a regra
        # rejeitou efetivamente o registo.
        #
        # NOT_EVALUATED não é um novo erro:
        # significa apenas que outra falha anterior
        # impediu esta regra de ser avaliada.
        if timing_result["validation_status"] == "REJECTED":
            errors.append(
                timing_result["error_code"]
            )

        # Se não encontramos nenhum erro, o registo é válido.
        if len(errors) == 0:
            final_status = "VALID"

        # Se existe pelo menos um erro, rejeitamos o registo.
        else:
            final_status = "REJECTED"

        # Guardamos o resultado consolidado.
        consolidated_results.append({
            "record_id": record_id,
            "validation_status": final_status,
            "errors": errors
        })

    # Devolvemos o relatório final.
    return consolidated_results