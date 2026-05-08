"""
DICOM de-identification helper (DICOM PS3.15 Annex E "Basic Application
Confidentiality Profile" — minimal, conservative subset).

This module is deliberately scoped to *metadata redaction* only. Pixel-level
de-identification (burned-in PHI on images) is a separate problem and is **not**
covered here.

Why this is its own module:

* PACS workflows in PHI environments must scrub demographics before any data
  leaves the hospital boundary or before training/eval datasets are exported.
* Keeping the redaction list as a small, audited table makes regulatory review
  much easier than scattering ``setattr`` calls across endpoints.

Usage::

    ds = pydicom.dcmread(path)
    redacted, report = deidentify_dataset(ds, replacement_id="anon-0001")
    redacted.save_as(out_path)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:  # pragma: no cover - typing only
    from pydicom.dataset import Dataset


# Tags to overwrite or clear. Each entry: (DICOM keyword, action).
# ``action`` is one of:
#   "blank"  -> set to empty string ("" or "ANONYMIZED" depending on VR)
#   "remove" -> delete the element entirely
#   "id"     -> replace with the supplied replacement_id
DEIDENTIFY_RULES: tuple[tuple[str, str], ...] = (
    # Patient identity
    ("PatientName", "blank"),
    ("PatientID", "id"),
    ("OtherPatientIDs", "remove"),
    ("OtherPatientIDsSequence", "remove"),
    ("PatientBirthDate", "blank"),
    ("PatientBirthTime", "remove"),
    ("PatientSex", "blank"),
    ("PatientAge", "blank"),
    ("PatientWeight", "remove"),
    ("PatientSize", "remove"),
    ("PatientAddress", "remove"),
    ("PatientTelephoneNumbers", "remove"),
    ("EthnicGroup", "remove"),
    ("Occupation", "remove"),
    ("AdditionalPatientHistory", "remove"),
    # Study / institution
    ("ReferringPhysicianName", "blank"),
    ("ReferringPhysicianAddress", "remove"),
    ("ReferringPhysicianTelephoneNumbers", "remove"),
    ("PhysiciansOfRecord", "remove"),
    ("PerformingPhysicianName", "remove"),
    ("OperatorsName", "remove"),
    ("InstitutionName", "blank"),
    ("InstitutionAddress", "remove"),
    ("InstitutionalDepartmentName", "remove"),
    # Free-text comments that often leak PHI
    ("StudyComments", "remove"),
    ("SeriesComments", "remove"),
    ("ImageComments", "remove"),
    ("PatientComments", "remove"),
    ("RequestedProcedureComments", "remove"),
    # Accession / order numbers — leave AccessionNumber but blank by default
    ("AccessionNumber", "blank"),
)


@dataclass
class DeidentificationReport:
    """Audit trail of a single de-identification pass."""

    replacement_id: str
    blanked: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    replaced: list[str] = field(default_factory=list)
    missing: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, object]:
        return {
            "replacement_id": self.replacement_id,
            "blanked": list(self.blanked),
            "removed": list(self.removed),
            "replaced": list(self.replaced),
            "missing": list(self.missing),
        }


def _blank_value(ds: "Dataset", keyword: str) -> None:
    """Best-effort blank that respects the data element's VR."""
    elem = ds.data_element(keyword)
    if elem is None:
        return
    if elem.VR in {"DA", "DT", "TM"}:
        elem.value = ""
    elif elem.VR in {"PN", "LO", "SH", "ST", "LT", "UT", "CS", "AE"}:
        elem.value = ""
    else:
        elem.value = ""


def deidentify_dataset(
    ds: "Dataset",
    *,
    replacement_id: str,
    extra_rules: Iterable[tuple[str, str]] = (),
) -> tuple["Dataset", DeidentificationReport]:
    """Return a redacted copy of ``ds`` plus an audit :class:`DeidentificationReport`.

    The original dataset is not modified.
    """
    import copy

    if not replacement_id:
        raise ValueError("replacement_id must be a non-empty string")

    redacted = copy.deepcopy(ds)
    report = DeidentificationReport(replacement_id=replacement_id)

    rules = list(DEIDENTIFY_RULES) + list(extra_rules)
    for keyword, action in rules:
        if keyword not in redacted:
            report.missing.append(keyword)
            continue
        if action == "remove":
            try:
                delattr(redacted, keyword)
            except AttributeError:
                # Fallback: clear via tag lookup
                tag = redacted.data_element(keyword).tag if redacted.data_element(keyword) else None
                if tag is not None:
                    del redacted[tag]
            report.removed.append(keyword)
        elif action == "id":
            setattr(redacted, keyword, replacement_id)
            report.replaced.append(keyword)
        elif action == "blank":
            _blank_value(redacted, keyword)
            report.blanked.append(keyword)
        else:  # pragma: no cover - guarded by static rules table
            raise ValueError(f"Unknown de-identification action: {action!r}")

    # Mark the dataset as de-identified per DICOM PS3.3 C.7.1.1
    redacted.PatientIdentityRemoved = "YES"
    redacted.DeidentificationMethod = "NeuroPredict basic profile (PS3.15 Annex E subset)"

    return redacted, report
