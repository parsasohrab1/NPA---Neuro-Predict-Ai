"""
FHIR R4 mappers: NeuroPredict-AI domain models → FHIR resource dicts.

We deliberately produce plain ``dict`` payloads (not ``fhir.resources`` model
instances) because:

* They serialise directly through FastAPI/JSON without depending on a specific
  pydantic version.
* They are trivially testable with ``assert dict == expected``.
* Keeping the surface narrow means we don't bind callers to the
  ``fhir.resources`` type system, which is heavy and version-sensitive.

Each helper is total: given a non-``None`` model, it returns a complete
resource dict. Search bundles are produced by :func:`build_searchset_bundle`.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any, Iterable, Mapping

if TYPE_CHECKING:  # pragma: no cover - type-only imports
    from ...models.medical_record import MedicalRecord
    from ...models.patient import Patient
    from ...models.prediction import Prediction


# --- Patient -----------------------------------------------------------------

_GENDER_MAP = {
    "male": "male",
    "female": "female",
    "other": "other",
}


def patient_to_fhir(patient: "Patient") -> dict[str, Any]:
    """Map a :class:`Patient` row to a FHIR R4 ``Patient`` resource dict."""
    if patient is None:
        raise ValueError("patient must not be None")

    gender_value = patient.gender.value if patient.gender else None
    fhir_gender = _GENDER_MAP.get(gender_value or "", "unknown")

    name: dict[str, Any] = {
        "use": "official",
        "family": patient.last_name,
        "given": [patient.first_name] if patient.first_name else [],
        "text": f"{patient.first_name} {patient.last_name}".strip(),
    }
    telecom: list[dict[str, Any]] = []
    if patient.email:
        telecom.append({"system": "email", "value": patient.email, "use": "home"})
    if patient.phone:
        telecom.append({"system": "phone", "value": patient.phone, "use": "mobile"})

    address: list[dict[str, Any]] = []
    if patient.address:
        address.append({"use": "home", "text": patient.address})

    birth: str | None = None
    if isinstance(patient.date_of_birth, (date, datetime)):
        birth = patient.date_of_birth.isoformat()[:10]
    elif patient.date_of_birth:
        birth = str(patient.date_of_birth)[:10]

    return {
        "resourceType": "Patient",
        "id": str(patient.id),
        "identifier": [
            {
                "use": "usual",
                "system": "urn:neuropredict:patient-id",
                "value": patient.patient_id,
            }
        ],
        "active": True,
        "name": [name],
        "telecom": telecom,
        "gender": fhir_gender,
        "birthDate": birth,
        "address": address,
    }


# --- Observation -------------------------------------------------------------

# (db_attr, LOINC code, display name, unit, ucum) — used to project a
# MedicalRecord into a list of clinically meaningful Observations.
# Selecting LOINCs is intentionally conservative: we expose only fields that
# are unambiguously coded. Unsupported attrs are skipped silently.
_OBSERVATION_MAP: tuple[tuple[str, str, str, str | None, str | None], ...] = (
    ("mmse_score", "72133-2", "Mini-Mental State Examination total score", "{score}", "{score}"),
    ("moca_score", "72172-0", "Montreal Cognitive Assessment total score", "{score}", "{score}"),
    ("blood_pressure_systolic", "8480-6", "Systolic blood pressure", "mmHg", "mm[Hg]"),
    ("blood_pressure_diastolic", "8462-4", "Diastolic blood pressure", "mmHg", "mm[Hg]"),
    ("heart_rate", "8867-4", "Heart rate", "/min", "/min"),
    ("respiratory_rate", "9279-1", "Respiratory rate", "/min", "/min"),
    ("temperature", "8310-5", "Body temperature", "Cel", "Cel"),
    ("oxygen_saturation", "59408-5", "Oxygen saturation in arterial blood by Pulse oximetry", "%", "%"),
    ("weight", "29463-7", "Body weight", "kg", "kg"),
    ("height", "8302-2", "Body height", "cm", "cm"),
    ("bmi", "39156-5", "Body mass index", "kg/m2", "kg/m2"),
    ("blood_glucose", "1558-6", "Fasting glucose [Mass/volume] in Serum or Plasma", "mg/dL", "mg/dL"),
    ("cholesterol_total", "2093-3", "Cholesterol [Mass/volume] in Serum or Plasma", "mg/dL", "mg/dL"),
)


def medical_record_to_observations(record: "MedicalRecord") -> list[dict[str, Any]]:
    """Project a :class:`MedicalRecord` to a list of FHIR ``Observation``\\s.

    Attributes that are ``None`` are skipped so the bundle only contains
    actually measured values.
    """
    if record is None:
        raise ValueError("record must not be None")

    effective = (
        record.visit_date.isoformat()
        if isinstance(record.visit_date, (date, datetime))
        else None
    )
    patient_ref = {"reference": f"Patient/{record.patient_id}"}

    out: list[dict[str, Any]] = []
    for attr, code, display, unit, ucum in _OBSERVATION_MAP:
        value = getattr(record, attr, None)
        if value is None:
            continue
        observation: dict[str, Any] = {
            "resourceType": "Observation",
            "id": f"medrec-{record.id}-{attr}",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "vital-signs" if attr.startswith(("blood_pressure", "heart_rate", "respiratory_rate", "temperature", "oxygen_saturation", "weight", "height", "bmi")) else "laboratory",
                        }
                    ]
                }
            ],
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": code,
                        "display": display,
                    }
                ],
                "text": display,
            },
            "subject": patient_ref,
            "valueQuantity": {
                "value": float(value),
                "unit": unit,
                "system": "http://unitsofmeasure.org",
                "code": ucum,
            },
        }
        if effective:
            observation["effectiveDateTime"] = effective
        out.append(observation)

    return out


# --- DiagnosticReport (from a Prediction) -----------------------------------

_RISK_LEVEL_DISPLAY = {
    "low": "Low risk",
    "medium": "Medium risk",
    "high": "High risk",
}


def prediction_to_diagnostic_report(prediction: "Prediction") -> dict[str, Any]:
    """Map a :class:`Prediction` to a FHIR R4 ``DiagnosticReport`` resource."""
    if prediction is None:
        raise ValueError("prediction must not be None")

    issued = (
        prediction.created_at.isoformat()
        if isinstance(prediction.created_at, (date, datetime))
        else datetime.utcnow().isoformat()
    )

    components: list[dict[str, Any]] = []
    if prediction.alzheimer_risk_score is not None:
        components.append(
            {
                "code": {
                    "coding": [
                        {
                            "system": "urn:neuropredict:risk",
                            "code": "alzheimer-risk-score",
                            "display": "Alzheimer risk score (0-1)",
                        }
                    ]
                },
                "valueQuantity": {
                    "value": float(prediction.alzheimer_risk_score),
                    "unit": "1",
                    "system": "http://unitsofmeasure.org",
                    "code": "1",
                },
            }
        )
    if prediction.parkinson_risk_score is not None:
        components.append(
            {
                "code": {
                    "coding": [
                        {
                            "system": "urn:neuropredict:risk",
                            "code": "parkinson-risk-score",
                            "display": "Parkinson risk score (0-1)",
                        }
                    ]
                },
                "valueQuantity": {
                    "value": float(prediction.parkinson_risk_score),
                    "unit": "1",
                    "system": "http://unitsofmeasure.org",
                    "code": "1",
                },
            }
        )

    conclusion_parts: list[str] = []
    if prediction.alzheimer_risk_level:
        conclusion_parts.append(
            f"Alzheimer: {_RISK_LEVEL_DISPLAY.get(prediction.alzheimer_risk_level.value, prediction.alzheimer_risk_level.value)}"
        )
    if prediction.parkinson_risk_level:
        conclusion_parts.append(
            f"Parkinson: {_RISK_LEVEL_DISPLAY.get(prediction.parkinson_risk_level.value, prediction.parkinson_risk_level.value)}"
        )

    return {
        "resourceType": "DiagnosticReport",
        "id": str(prediction.id),
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                        "code": "NRO",
                        "display": "Neurology",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "urn:neuropredict:report",
                    "code": "neurodegenerative-risk",
                    "display": "Neurodegenerative disease risk assessment",
                }
            ],
            "text": "NeuroPredict-AI risk assessment",
        },
        "subject": {"reference": f"Patient/{prediction.patient_id}"},
        "effectiveDateTime": issued,
        "issued": issued,
        "performer": [
            {
                "display": (
                    f"{prediction.model_name or 'NeuroPredict-AI'} "
                    f"({prediction.model_version or 'unknown'})"
                ).strip()
            }
        ],
        "conclusion": "; ".join(conclusion_parts) or "No risk levels recorded.",
        "result": components,
    }


# --- Bundle ------------------------------------------------------------------

def build_searchset_bundle(
    resources: Iterable[Mapping[str, Any]],
    *,
    base_url: str,
) -> dict[str, Any]:
    """Wrap an iterable of resource dicts in a ``Bundle`` with ``type: searchset``.

    ``base_url`` is used to construct absolute ``fullUrl`` entries.
    """
    entries: list[dict[str, Any]] = []
    materialised = list(resources)
    for resource in materialised:
        rt = resource.get("resourceType", "Resource")
        rid = resource.get("id", "")
        entries.append(
            {
                "fullUrl": f"{base_url.rstrip('/')}/{rt}/{rid}",
                "resource": resource,
                "search": {"mode": "match"},
            }
        )
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(materialised),
        "entry": entries,
    }


# --- CapabilityStatement -----------------------------------------------------

def build_capability_statement(*, fhir_version: str = "4.0.1") -> dict[str, Any]:
    """Return a minimal but accurate ``CapabilityStatement`` for our server."""
    return {
        "resourceType": "CapabilityStatement",
        "status": "active",
        "date": datetime.utcnow().date().isoformat(),
        "kind": "instance",
        "publisher": "NeuroPredict-AI",
        "software": {"name": "NeuroPredict-AI FHIR adapter"},
        "fhirVersion": fhir_version,
        "format": ["application/fhir+json", "json"],
        "rest": [
            {
                "mode": "server",
                "resource": [
                    {
                        "type": "Patient",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"},
                        ],
                        "searchParam": [
                            {"name": "_id", "type": "token"},
                            {"name": "identifier", "type": "token"},
                        ],
                    },
                    {
                        "type": "Observation",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"},
                        ],
                        "searchParam": [
                            {"name": "subject", "type": "reference"},
                            {"name": "code", "type": "token"},
                        ],
                    },
                    {
                        "type": "DiagnosticReport",
                        "interaction": [
                            {"code": "read"},
                            {"code": "search-type"},
                        ],
                        "searchParam": [
                            {"name": "subject", "type": "reference"},
                            {"name": "status", "type": "token"},
                        ],
                    },
                    {
                        "type": "ImagingStudy",
                        "interaction": [{"code": "search-type"}],
                        "searchParam": [
                            {"name": "subject", "type": "reference"},
                            {"name": "modality", "type": "token"},
                        ],
                    },
                ],
            }
        ],
    }
