# Vendor Risk Assessment — Template

**ALVO Platform**  
**Assessment Date:** [DATE]  
**Assessed by:** Compliance Officer  
**Next Review:** [DATE + 12 months]

---

## 1. Vendor Information

| Field | Value |
|-------|-------|
| **Vendor Name** | |
| **Service Description** | |
| **Website** | |
| **Primary Contact** | |
| **Security Contact** | |
| **Data Processing Location** | |
| **Sub-processors** | |

---

## 2. Data Assessment

### 2.1 Data Categories Shared

| Data Category | Shared? | Volume | Sensitivity |
|--------------|---------|--------|-------------|
| User PII | ☐ Yes ☐ No | | ☐ Low ☐ Medium ☐ High |
| Authentication data | ☐ Yes ☐ No | | ☐ Low ☐ Medium ☐ High |
| Financial data | ☐ Yes ☐ No | | ☐ Low ☐ Medium ☐ High |
| User content/inputs | ☐ Yes ☐ No | | ☐ Low ☐ Medium ☐ High |
| System logs | ☐ Yes ☐ No | | ☐ Low ☐ Medium ☐ High |
| Analytics data | ☐ Yes ☐ No | | ☐ Low ☐ Medium ☐ High |

### 2.2 Data Flow

```
[Describe data flow: ALVO → Vendor → Storage/Processing → Return]
```

---

## 3. Security Assessment

### 3.1 Certifications & Compliance

| Certification | Status | Expiry |
|--------------|--------|--------|
| SOC2 Type II | ☐ Yes ☐ No ☐ Requested | |
| ISO 27001 | ☐ Yes ☐ No ☐ Requested | |
| GDPR Compliant | ☐ Yes ☐ No ☐ Partial | |
| HIPAA | ☐ Yes ☐ No ☐ N/A | |
| PCI DSS | ☐ Yes ☐ No ☐ N/A | |
| FedRAMP | ☐ Yes ☐ No ☐ N/A | |

### 3.2 Security Controls

| Control Area | Implemented | Evidence |
|-------------|-------------|----------|
| Encryption at rest | ☐ Yes ☐ No ☐ Partial | |
| Encryption in transit | ☐ Yes ☐ No ☐ Partial | |
| Access controls | ☐ Yes ☐ No ☐ Partial | |
| MFA available | ☐ Yes ☐ No ☐ Partial | |
| Logging & monitoring | ☐ Yes ☐ No ☐ Partial | |
| Incident response plan | ☐ Yes ☐ No ☐ Partial | |
| Penetration testing | ☐ Yes ☐ No ☐ Partial | |
| Vulnerability management | ☐ Yes ☐ No ☐ Partial | |
| Business continuity | ☐ Yes ☐ No ☐ Partial | |
| Data backup | ☐ Yes ☐ No ☐ Partial | |

---

## 4. Contractual Assessment

| Requirement | Included | Notes |
|------------|----------|-------|
| Data Processing Agreement | ☐ Yes ☐ No | |
| SLA commitments | ☐ Yes ☐ No | |
| Data breach notification | ☐ Yes ☐ No | |
| Audit rights | ☐ Yes ☐ No | |
| Data deletion on termination | ☐ Yes ☐ No | |
| Sub-processor restrictions | ☐ Yes ☐ No | |
| Liability provisions | ☐ Yes ☐ No | |
| GDPR compliance clause | ☐ Yes ☐ No | |

---

## 5. Risk Scoring

### 5.1 Likelihood Assessment

| Factor | Score (1-5) |
|--------|-------------|
| Data sensitivity | |
| Volume of data | |
| Access level | |
| Integration depth | |
| Replaceability | |

### 5.2 Impact Assessment

| Factor | Score (1-5) |
|--------|-------------|
| Confidentiality impact | |
| Integrity impact | |
| Availability impact | |
| Regulatory impact | |
| Reputational impact | |

### 5.3 Risk Score Calculation

| Metric | Value |
|--------|-------|
| **Likelihood Score** | /25 |
| **Impact Score** | /25 |
| **Risk Score** | /125 |
| **Risk Level** | ☐ Critical ☐ High ☐ Medium ☐ Low |

---

## 6. Risk Level Matrix

| Risk Score | Risk Level | Required Actions |
|-----------|------------|------------------|
| 80-125 | **Critical** | Executive approval, enhanced monitoring, quarterly review |
| 50-79 | **High** | Security Architect approval, semi-annual review |
| 25-49 | **Medium** | Compliance Officer approval, annual review |
| 1-24 | **Low** | Standard procurement, annual review |

---

## 7. Findings & Recommendations

### 7.1 Identified Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### 7.2 Required Remediations

| # | Issue | Priority | Deadline | Owner |
|---|-------|----------|----------|-------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## 8. Approval

| Role | Name | Decision | Date |
|------|------|----------|------|
| Compliance Officer | | ☐ Approved ☐ Rejected ☐ Conditional | |
| Security Architect | | ☐ Approved ☐ Rejected ☐ Conditional | |
| CTO (if Critical/High) | | ☐ Approved ☐ Rejected ☐ Conditional | |

---

## 9. Monitoring Schedule

| Activity | Frequency | Next Due |
|----------|-----------|----------|
| Security certification review | Annual | |
| Contract review | Annual | |
| Risk reassessment | Annual | |
| Incident review | As needed | |
| DPA compliance check | Quarterly | |

---

*Completed assessments should be stored in: compliance/vendor-assessments/[vendor-name].md*
