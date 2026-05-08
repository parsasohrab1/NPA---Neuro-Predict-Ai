"""
Sanity tests for the DICOM de-identification helper.

We construct an in-memory pydicom Dataset (no real .dcm file required) so the
test does not depend on having a sample DICOM in the repo. ``pydicom`` is a
required dependency in ``backend/requirements.txt`` already.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def _build_dataset():
    pydicom = pytest.importorskip("pydicom")
    ds = pydicom.dataset.Dataset()
    ds.PatientName = "Doe^Jane"
    ds.PatientID = "MRN-PHI-001"
    ds.PatientBirthDate = "19600515"
    ds.PatientSex = "F"
    ds.ReferringPhysicianName = "Smith^John"
    ds.InstitutionName = "PHI Hospital"
    ds.StudyComments = "history of dementia"
    ds.AccessionNumber = "ACC-123"
    return ds


def test_deidentify_basic_redaction() -> None:
    pytest.importorskip("pydicom")
    from app.services.integration.dicom_deidentify import deidentify_dataset

    ds = _build_dataset()
    redacted, report = deidentify_dataset(ds, replacement_id="anon-0001")

    assert str(redacted.PatientName) == ""
    assert redacted.PatientID == "anon-0001"
    assert redacted.PatientBirthDate == ""
    assert "ReferringPhysicianName" not in redacted or str(redacted.ReferringPhysicianName) == ""
    assert "StudyComments" not in redacted
    assert redacted.PatientIdentityRemoved == "YES"
    assert "PatientID" in report.replaced
    assert "PatientName" in report.blanked
    assert "StudyComments" in report.removed


def test_deidentify_does_not_mutate_input() -> None:
    pytest.importorskip("pydicom")
    from app.services.integration.dicom_deidentify import deidentify_dataset

    ds = _build_dataset()
    deidentify_dataset(ds, replacement_id="anon-2")

    assert str(ds.PatientName) == "Doe^Jane"
    assert ds.PatientID == "MRN-PHI-001"
    assert ds.PatientBirthDate == "19600515"


def test_deidentify_requires_replacement_id() -> None:
    pytest.importorskip("pydicom")
    from app.services.integration.dicom_deidentify import deidentify_dataset

    ds = _build_dataset()
    with pytest.raises(ValueError):
        deidentify_dataset(ds, replacement_id="")


def test_deidentify_extra_rules() -> None:
    pytest.importorskip("pydicom")
    from app.services.integration.dicom_deidentify import deidentify_dataset

    ds = _build_dataset()
    ds.add_new(0x00100040, "CS", "F")  # PatientSex tag, already covered

    _, report = deidentify_dataset(
        ds,
        replacement_id="anon-3",
        extra_rules=[("AccessionNumber", "remove")],
    )
    assert "AccessionNumber" in report.removed
