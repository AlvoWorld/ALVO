# LLM Vendor Security Assessment
**Document ID:** ALVO-VAR-LLM-001  
**Version:** 1.0  
**Classification:** Confidential  
**Assessment Date:** _______________  
**Assessor:** Compliance Officer  

---

## 1. Vendor Information

| Field | Value |
|-------|-------|
| **Vendor Name** | |
| **Service Description** | LLM API / AI Processing |
| **Website** | |
| **Primary Contact** | |
| **Security Contact** | |
| **Data Processing Location(s)** | |
| **Parent Company** | |

---

## 2. Assessment Summary

| Category | Score (1-5) | Status |
|----------|-------------|--------|
| Security Controls | | |
| Data Protection | | |
| Compliance & Certifications | | |
| Incident Response | | |
| Business Continuity | | |
| **Overall Score** | | |

**Recommendation:** ☐ Approved | ☐ Approved with Conditions | ☐ Not Approved

---

## 3. Security Controls Assessment

### 3.1 Infrastructure Security

| Question | Response | Evidence |
|----------|----------|----------|
| Is infrastructure SOC 2 Type II certified? | | |
| Is ISO 27001 certification maintained? | | |
| Are regular penetration tests conducted? | | |
| Is encryption at rest implemented (AES-256)? | | |
| Is TLS 1.2+ enforced for all API communications? | | |
| Are encryption keys managed securely (HSM/KMS)? | | |

### 3.2 Access Controls

| Question | Response | Evidence |
|----------|----------|----------|
| Is MFA required for all employee access? | | |
| Are access reviews conducted regularly? | | |
| Is privileged access logged and monitored? | | |
| Is background screening performed for employees? | | |
| Are vendor/third-party access controls in place? | | |

### 3.3 Data Handling

| Question | Response | Evidence |
|----------|----------|----------|
| Is customer data logically isolated? | | |
| Are API inputs/outputs logged? If so, retention? | | |
| Is data used for model training? (opt-out available?) | | |
| What is data retention period? | | |
| Is data deleted upon contract termination? | | |
| Are data deletion certificates provided? | | |

---

## 4. Compliance & Legal

### 4.1 GDPR Compliance

| Question | Response | Evidence |
|----------|----------|----------|
| Is a DPA (Data Processing Agreement) available? | | |
| Are Standard Contractual Clauses (SCCs) offered? | | |
| Has a Transfer Impact Assessment been completed? | | |
| Is a DPO designated? | | |
| Are data subject rights supported? | | |
| Is data processing documented per Art. 30? | | |

### 4.2 Certifications & Audits

| Certification/Audit | Status | Expiry Date | Evidence |
|---------------------|--------|-------------|----------|
| SOC 2 Type II | | | |
| ISO 27001 | | | |
| ISO 27701 | | | |
| GDPR Compliance | | | |
| HIPAA (if applicable) | | | |
| CSA STAR | | | |

---

## 5. Incident Response & Business Continuity

| Question | Response | Evidence |
|----------|----------|----------|
| Is an incident response plan documented? | | |
| What is the breach notification timeline? | | |
| Is 24/7 security monitoring in place? | | |
| What is the SLA for incident communication? | | |
| Is a business continuity plan maintained? | | |
| What is the RPO/RTO for service recovery? | | |
| Are backups geographically distributed? | | |

---

## 6. Contractual Requirements

### 6.1 Required Contract Terms

| Term | Included | Notes |
|------|----------|-------|
| Data Processing Agreement (DPA) | ☐ | |
| Standard Contractual Clauses | ☐ | |
| Breach notification (<72 hours) | ☐ | |
| Audit rights | ☐ | |
| Data deletion upon termination | ☐ | |
| Sub-processor notification | ☐ | |
| Liability for data breaches | ☐ | |
| Insurance requirements | ☐ | |

### 6.2 SLA Requirements

| Metric | Required | Agreed |
|--------|----------|--------|
| API Uptime | ≥99.9% | |
| Latency (p95) | <500ms | |
| Support Response (Critical) | <1 hour | |
| Support Response (High) | <4 hours | |
| Incident Notification | <24 hours | |

---

## 7. Risk Assessment

### 7.1 Identified Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Data breach at vendor | | | |
| Unauthorized data access | | | |
| Data used for training without consent | | | |
| Service unavailability | | | |
| Regulatory non-compliance | | | |
| Vendor lock-in | | | |
| Sub-processor risk | | | |

### 7.2 Data Flow Diagram

```
[ALVO Platform] → [TLS 1.3] → [Vendor API] → [Vendor Infrastructure]
                                              ↓
                                    [Data Processing/Storage]
                                              ↓
                                    [Response] → [ALVO Platform]
```

*Document specific data elements transmitted:*
- 
- 
- 

---

## 8. Recommendations & Conditions

### 8.1 Findings

| # | Finding | Severity | Recommendation |
|---|---------|----------|----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

### 8.2 Conditions for Approval (if applicable)

1. 
2. 
3. 

### 8.3 Required Remediation Timeline

| Finding | Deadline | Owner |
|---------|----------|-------|
| | | |

---

## 9. Approval

| Role | Name | Date | Decision |
|------|------|------|----------|
| Compliance Officer | | | ☐ Approve ☐ Conditional ☐ Reject |
| Security Architect | | | ☐ Approve ☐ Conditional ☐ Reject |
| CTO | | | ☐ Approve ☐ Conditional ☐ Reject |

---

## 10. Reassessment Schedule

| Event | Action Required |
|-------|-----------------|
| Annual review | Full reassessment |
| Security incident at vendor | Immediate review |
| Contract renewal | Reassessment required |
| Service scope change | Impact assessment |
| Regulatory change | Compliance review |

**Next Scheduled Review:** _______________

---

*This document is the property of ALVO Platform and contains confidential information.*
