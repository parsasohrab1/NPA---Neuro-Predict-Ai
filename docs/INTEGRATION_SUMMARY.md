# خلاصه یکپارچه‌سازی - NeuroPredict-AI

> **وضعیت کلی:** scaffolding / partial — سازنده‌های پیام و منبع محلی کار می‌کنند؛
> ارسال/دریافت remote بدون پیکربندی صریح، دیگر «موفقیت جعلی» برنمی‌گرداند
> (HTTP 501/503 با `not_configured` / `not_implemented`).

## وضعیت پیاده‌سازی (صادقانه)

### 1. HL7 FHIR Integration — partial

**Local (DB-backed) adapters:**
- `GET /api/v1/fhir/Patient`, `Observation`, `DiagnosticReport` — از دیتابیس NeuroPredict
- `GET /api/v1/fhir/metadata` — CapabilityStatement
- سازنده‌های منبع در `fhir_service.py` (Patient / Observation / …)

**Remote FHIR client:**
- نیازمند `HL7_FHIR_ENDPOINT`
- `GET /api/v1/fhir/remote/{type}` و `.../{id}` با httpx
- بدون env → HTTP 503 `not_configured`
- `GET /api/v1/fhir/ImagingStudy` محلی → HTTP 501 `not_implemented` (ایندکس DICOM هنوز FHIR نیست)

### 2. PACS Integration (DICOM) — partial / scaffolding

**Local (بدون PACS):**
- Parse metadata و validate فایل DICOM (`pydicom`) — کار می‌کند

**Remote DIMSE (C-FIND / C-MOVE / C-STORE / MWL):**
- نیازمند `PACS_SERVER_URL` + بسته اختیاری `pynetdicom`
- بدون پیکربندی → HTTP 503 `not_configured` (نه لیست خالی 200)
- با پیکربندی ولی بدون پیاده‌سازی کامل DIMSE → HTTP 501 `not_implemented`

### 3. HL7 v2 — partial

**Local builders/parsers:** ADT/ORU ساخت و parse — کار می‌کند

**Send (MLLP):**
- اگر `HL7_MLLP_HOST` تنظیم شده باشد → TCP MLLP send حداقلی
- در غیر این صورت → HTTP 503 `not_configured` (دیگر `return True` جعلی نیست)

### 4. EHR/HIS Integration — partial

- کلاینت REST با retry/timeout در `ehr_service.py`
- بدون `EHR_API_URL` نباید موفقیت جعلی برگردانده شود

### 5. Configuration

| Variable | Purpose |
|----------|---------|
| `PACS_SERVER_URL` / `PACS_AE_TITLE` | Remote PACS DIMSE peer |
| `HL7_FHIR_ENDPOINT` | Remote FHIR base URL |
| `HL7_FHIR_BASE_URL` | Local FHIR resource base for Bundle URLs |
| `HL7_MLLP_HOST` / `HL7_MLLP_PORT` | HL7 v2 MLLP TCP send |
| `HL7_SERVER_URL` | Optional legacy / destination override |
| `EHR_API_URL` / `EHR_API_KEY` | EHR REST |

### 6. Dependencies

- `pydicom` — DICOM local parse/validate
- `fhir.resources` — FHIR resource models
- `httpx` — remote FHIR/EHR HTTP
- `pynetdicom` — **optional**, required for real DIMSE (not bundled by default)

---

## جدول وضعیت

| Feature | Status | Notes |
|---------|--------|-------|
| HL7 FHIR local (Patient/Obs/DR) | Partial | DB-backed read/search |
| HL7 FHIR remote client | Partial | httpx when `HL7_FHIR_ENDPOINT` set |
| ImagingStudy FHIR | Not implemented | 501 explicit |
| PACS local validate/parse | Working | No remote needed |
| PACS DIMSE | Scaffolding | 503/501 honest errors |
| EHR/HIS | Partial | REST client; needs URL |
| HL7 v2 build/parse | Working | Local only |
| HL7 v2 MLLP send | Partial | Minimal TCP when host set |
| Contract tests | Added | `tests/integration/test_integration_contracts.py` |

---

## نکات مهم

1. **هرگز به HTTP 200 خالی برای remote اعتماد نکنید** — وضعیت را از `status` / HTTP code بخوانید
2. **Authentication** برای EHR از API keys
3. **Timeout** برای درخواست‌های خارجی
4. **Security** — HTTPS برای تمام peerهای production

---

## گام‌های بعدی

1. پیاده‌سازی کامل DIMSE با pynetdicom
2. ACK کامل HL7 MLLP و retry
3. ImagingStudy از ایندکس DICOM
4. تست قرارداد با WireMock / شبیه‌ساز PACS
