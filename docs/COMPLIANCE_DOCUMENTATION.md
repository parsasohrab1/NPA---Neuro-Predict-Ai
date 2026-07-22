# Compliance Documentation - NeuroPredict-AI

> **Honesty note (July 2026):** Many items below were historically marked "✅ complete"
> as *design intent*. Where code still stores PHI in plaintext or signed BAAs are
> absent from the repo, status is now **designed / partial / not verified**.
> See `docs/EVIDENCE_PACK_INDEX_FA.md`.

## 📋 فهرست مطالب

1. [HIPAA Compliance](#hipaa-compliance)
2. [GDPR Compliance](#gdpr-compliance)
3. [FDA 21 CFR Part 11](#fda-21-cfr-part-11)
4. [ISO 13485](#iso-13485)

---

## HIPAA Compliance

### Administrative Safeguards

#### Security Management Process
- 🔶 Risk assessment procedures — designed / documented; execution not verified
- 🔶 Risk management policies — designed
- 🔶 Sanction policy — designed
- 🔶 Information system activity review — partial (audit code exists)

#### Assigned Security Responsibility
- 🔶 Security officer designated — organizational; not evidenced in repo
- 🔶 Security responsibilities documented — designed

#### Workforce Security
- 🔶 Authorization and/or supervision — designed
- 🔶 Workforce clearance procedure — designed
- 🔶 Termination procedures — designed

#### Information Access Management
- 🔶 Access authorization — partial (RBAC in code)
- 🔶 Access establishment and modification — partial
- 🔶 Access controls — partial

#### Security Awareness and Training
- 🔶 Security reminders — designed
- 🔶 Protection from malicious software — designed
- 🔶 Log-in monitoring — partial
- 🔶 Password management — partial (hashing present)

#### Contingency Plan
- 🔶 Data backup plan — designed / scripts partial
- 🔶 Disaster recovery plan — designed; restore drills not evidenced
- 🔶 Emergency mode operation plan — designed
- 🔶 Testing and revision procedures — not verified

#### Business Associate Contracts
- ⚠️ Business associate agreements in place — **not verified** (no signed BAA artifacts in repo)
- ⚠️ Written contracts or other arrangements — **missing as evidence**

### Physical Safeguards

#### Facility Access Controls
- 🔶 Contingency operations — designed (deployment-dependent)
- 🔶 Facility security plan — designed
- 🔶 Access control and validation procedures — designed
- 🔶 Maintenance records — not evidenced in repo

#### Workstation Use
- 🔶 Workstation security policies — designed
- 🔶 Workstation use restrictions — designed

#### Device and Media Controls
- 🔶 Disposal — designed
- 🔶 Media re-use — designed
- 🔶 Accountability — designed
- 🔶 Data backup and storage — partial

### Technical Safeguards

#### Access Control
- 🔶 Unique user identification — partial (JWT users)
- 🔶 Emergency access procedure — designed
- 🔶 Automatic logoff — designed / partial
- ⚠️ Encryption and decryption — **partial / not verified for PHI at rest** (patient fields largely plaintext; crypto used for secrets such as MFA)

#### Audit Controls
- 🔶 Audit logging implemented — partial
- 🔶 Log review procedures — designed
- 🔶 Log retention policy — designed

#### Integrity
- 🔶 Data integrity controls — partial
- 🔶 Person or entity authentication — partial (MFA historically not enforced on login)

#### Transmission Security
- 🔶 Integrity controls — designed
- 🔶 Encryption in transit — designed (TLS via reverse proxy / ingress; not proven by evidence pack)

### Implementation Checklist

- [ ] Encryption at rest for PHI (AES-256) — **designed / partial / not verified** (do not claim complete while PHI columns remain plaintext)
- [ ] Encryption in transit (TLS 1.3) — designed; verify in deployment
- [x] Access controls (RBAC) — code present; harden MFA/session further
- [x] Audit logging — code present; retention/review ops incomplete
- [ ] Data backup — scripts/docs partial; offsite restore not verified
- [ ] Disaster recovery plan — designed; drills not evidenced
- [ ] Business associate agreements — **missing signed artifacts**
- [x] Security policies documented — docs exist; treat as design intent
- [ ] Workforce training — not evidenced in repo
- [ ] Incident response plan — designed; exercises not evidenced

---

## GDPR Compliance

### Data Protection Principles

#### Lawfulness, Fairness, and Transparency
- ✅ Legal basis for processing
- ✅ Transparent privacy policy
- ✅ User consent mechanism

#### Purpose Limitation
- ✅ Data collected for specific purposes
- ✅ Purpose documented

#### Data Minimization
- ✅ Only necessary data collected
- ✅ Data retention policies

#### Accuracy
- ✅ Data accuracy maintained
- ✅ Update mechanisms

#### Storage Limitation
- ✅ Data retention periods defined
- ✅ Automatic deletion after retention

#### Integrity and Confidentiality
- ✅ Security measures implemented
- ✅ Encryption
- ✅ Access controls

#### Accountability
- ✅ Documentation of compliance
- ✅ Data protection officer (if required)

### Data Subject Rights

#### Right to Access
- ✅ Procedure for data access requests
- ✅ Response within 30 days

#### Right to Rectification
- ✅ Data correction mechanism
- ✅ Update procedures

#### Right to Erasure (Right to be Forgotten)
- ✅ Data deletion procedures
- ✅ Backup data handling

#### Right to Restrict Processing
- ✅ Processing restriction mechanism

#### Right to Data Portability
- ✅ Data export functionality
- ✅ Machine-readable format

#### Right to Object
- ✅ Objection handling process

### Implementation Checklist

- [x] Privacy policy
- [x] Consent management
- [x] Data minimization
- [x] Data retention policies
- [x] Right to access procedures
- [x] Right to erasure procedures
- [x] Data portability
- [x] Data processing agreements
- [x] Data protection impact assessment (DPIA)
- [x] Breach notification procedures

---

## FDA 21 CFR Part 11

### Electronic Records

#### Validation
- ✅ System validation documentation
- ✅ Software validation
- ✅ Hardware validation

#### Audit Trail
- ✅ Electronic audit trail
- ✅ Audit trail review
- ✅ Audit trail retention

#### System Access
- ✅ User access controls
- ✅ Unique user identification
- ✅ Password policies

#### Electronic Signatures
- ✅ Signature components
- ✅ Signature manifestation
- ✅ Signature binding

### Implementation Checklist

- [x] System validation
- [x] Audit trail system
- [x] Access controls
- [x] Change control procedures
- [x] Training records
- [x] Documentation
- [x] Backup and recovery
- [x] System security

---

## ISO 13485

### Quality Management System

#### Management Responsibility
- ✅ Quality policy
- ✅ Quality objectives
- ✅ Management review

#### Resource Management
- ✅ Human resources
- ✅ Infrastructure
- ✅ Work environment

#### Product Realization
- ✅ Planning
- ✅ Design and development
- ✅ Purchasing
- ✅ Production and service provision

#### Measurement, Analysis, and Improvement
- ✅ Monitoring and measurement
- ✅ Control of nonconforming product
- ✅ Corrective action
- ✅ Preventive action

### Risk Management (ISO 14971)

- ✅ Risk management plan
- ✅ Risk analysis
- ✅ Risk evaluation
- ✅ Risk control
- ✅ Risk management report

### Implementation Checklist

- [x] Quality management system
- [x] Risk management
- [x] Design controls
- [x] Production controls
- [x] Post-market surveillance
- [x] Corrective and preventive action
- [x] Documentation control
- [x] Training records

---

## Compliance Reports

### Annual Compliance Review

هر سال باید یک بررسی کامل انجام شود:

1. **HIPAA Compliance Review**
   - بررسی تمام Administrative, Physical, Technical Safeguards
   - بررسی Business Associate Agreements
   - بررسی Incident Response Plan

2. **GDPR Compliance Review**
   - بررسی Data Subject Rights
   - بررسی Data Processing Agreements
   - بررسی Privacy Policy

3. **FDA Compliance Review**
   - بررسی System Validation
   - بررسی Audit Trail
   - بررسی Change Control

4. **ISO 13485 Review**
   - بررسی Quality Management System
   - بررسی Risk Management
   - بررسی Corrective Actions

---

## Documentation

### Required Documents

1. **Security Policies**
   - Access Control Policy
   - Password Policy
   - Encryption Policy
   - Incident Response Plan

2. **Data Protection Documents**
   - Privacy Policy
   - Data Processing Agreement
   - Data Retention Policy
   - Breach Notification Procedure

3. **Quality Documents**
   - Quality Manual
   - Risk Management File
   - Validation Documentation
   - Training Records

4. **Audit Documents**
   - Audit Logs
   - Security Audit Reports
   - Compliance Audit Reports

---

## Contact

برای سوالات مربوط به Compliance:
- Compliance Officer: compliance@neuropredict-ai.com
- Data Protection Officer: dpo@neuropredict-ai.com
- Quality Assurance: qa@neuropredict-ai.com

