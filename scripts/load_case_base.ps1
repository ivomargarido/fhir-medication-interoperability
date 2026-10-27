# ============================================================
# LOAD CASE BASE
# ============================================================
#
# Este script carrega no HAPI FHIR Server local todos os
# recursos que constituem o caso base do projeto.
#
# O objetivo é evitar ter de executar manualmente um POST
# para cada recurso sempre que o servidor reinicia.
#
# IMPORTANTE:
# Este script pressupõe que o HAPI FHIR Server já está
# disponível em:
#
# http://localhost:8080/fhir
#
# ============================================================


# ------------------------------------------------------------
# 1. CONFIGURAÇÃO
# ------------------------------------------------------------

# Endpoint base do nosso servidor FHIR local.
$FhirBaseUrl = "http://localhost:8080/fhir"

# PSScriptRoot corresponde à pasta onde este script está:
#
# fhir-medication-interoperability/scripts/
#
# Ao subir um nível chegamos à raiz do projeto.
$ProjectRoot = Split-Path -Parent $PSScriptRoot


# ------------------------------------------------------------
# 2. LISTA DOS RECURSOS DO CASO BASE
# ------------------------------------------------------------

# Os recursos são carregados numa ordem lógica:
#
# primeiro os recursos-base;
# depois os recursos clínicos que dependem deles.
#
# Existem 11 ficheiros JSON porque temos
# quatro Practitioner separados.

$Resources = @(

    # Patient
    @{
        Type = "Patient"
        File = "data\fhir\Patient\PAT001.json"
        Label = "PAT001"
    },

    # Practitioners
    @{
        Type = "Practitioner"
        File = "data\fhir\Practitioner\PRAC001.json"
        Label = "PRAC001"
    },

    @{
        Type = "Practitioner"
        File = "data\fhir\Practitioner\PRAC002.json"
        Label = "PRAC002"
    },

    @{
        Type = "Practitioner"
        File = "data\fhir\Practitioner\PRAC003.json"
        Label = "PRAC003"
    },

    @{
        Type = "Practitioner"
        File = "data\fhir\Practitioner\PRAC004.json"
        Label = "PRAC004"
    },

    # Medication
    @{
        Type = "Medication"
        File = "data\fhir\Medication\MED001.json"
        Label = "MED001"
    },

    # Encounters
    @{
        Type = "Encounter"
        File = "data\fhir\Encounter\ER-E001.json"
        Label = "ER-E001"
    },

    @{
        Type = "Encounter"
        File = "data\fhir\Encounter\IP-E001.json"
        Label = "IP-E001"
    },

    # MedicationRequest
    @{
        Type = "MedicationRequest"
        File = "data\fhir\MedicationRequest\ER-RX001.json"
        Label = "ER-RX001"
    },

    # MedicationDispense
    @{
        Type = "MedicationDispense"
        File = "data\fhir\MedicationDispense\PH-D001.json"
        Label = "PH-D001"
    },

    # MedicationAdministration
    @{
        Type = "MedicationAdministration"
        File = "data\fhir\MedicationAdministration\ER-ADM001.json"
        Label = "ER-ADM001"
    }
)


# ------------------------------------------------------------
# 3. CARREGAR OS RECURSOS
# ------------------------------------------------------------

foreach ($Resource in $Resources) {

    # Construímos o caminho completo para o ficheiro JSON.
    $FilePath = Join-Path $ProjectRoot $Resource.File

    # Endpoint correspondente ao tipo de recurso.
    #
    # Exemplo:
    # http://localhost:8080/fhir/Patient
    $Url = "$FhirBaseUrl/$($Resource.Type)"

    Write-Host ""
    Write-Host "Loading $($Resource.Type) $($Resource.Label)..."

    # Lemos o JSON exatamente como foi gerado
    # pelo nosso pipeline.
    $JsonBody = Get-Content `
        -Path $FilePath `
        -Raw `
        -Encoding UTF8

    # Fazemos o POST ao servidor FHIR.
    #
    # Invoke-RestMethod converte automaticamente
    # a resposta JSON para um objeto PowerShell.
    $Response = Invoke-RestMethod `
        -Method POST `
        -Uri $Url `
        -ContentType "application/fhir+json" `
        -Headers @{
            Accept = "application/fhir+json"
        } `
        -Body $JsonBody

    # Mostramos o resource.id atribuído pelo HAPI.
    Write-Host (
        "OK: {0} -> {1}/{2}" -f `
        $Resource.Label,
        $Resource.Type,
        $Response.id
    )
}


# ------------------------------------------------------------
# 4. FIM
# ------------------------------------------------------------

Write-Host ""
Write-Host "Case base loaded successfully."