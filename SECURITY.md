# Security Policy

<div align="center">

![Security](https://img.shields.io/badge/Security-Policy-red?style=for-the-badge&logo=shield&logoColor=white)
![Version](https://img.shields.io/badge/Version-3.3.4-006600?style=for-the-badge)

**PDBOT Security Guidelines & Vulnerability Reporting**

</div>

---

## 🛡️ Supported Versions

| Version | Status | Support Level |
|---------|--------|---------------|
| 3.3.x | ✅ Current | Full support - security patches & features |
| 2.5.x | ⚠️ Legacy | Critical security fixes only |
| < 2.5.0 | ❌ Unsupported | Please upgrade to latest version |

---

## 🔒 Security Measures

### Data Protection

| Measure | Implementation | Status |
|---------|----------------|--------|
| **No PII Storage** | User data processed in-memory only | ✅ Active |
| **Session Isolation** | Each session completely isolated | ✅ Active |
| **Memory Cleanup** | Data cleared on session end | ✅ Active |
| **No Query Logging** | User queries not persisted | ✅ Active |
| **Source-Only Answers** | All responses from Manual directly | ✅ Active |

### Input Validation

| Security Measure | Implementation | Status |
|------------------|----------------|--------|
| Query Length Limit | Maximum 2000 characters | ✅ Active |
| Special Character Filter | Dangerous characters sanitized | ✅ Active |
| SQL Injection Prevention | Parameterized queries | ✅ Active |
| XSS Prevention | HTML entity encoding | ✅ Active |
| Command Injection Block | Shell metacharacter filtering | ✅ Active |
| Path Traversal Prevention | Filename validation | ✅ Active |

### Content Safety

| Protection Type | Coverage | Status |
|-----------------|----------|--------|
| **Bribery/Corruption Detection** | 100% blocked | ✅ Active |
| **Fund Misuse Detection** | 100% blocked | ✅ Active |
| **Sexual Content Filter** | 25+ patterns | ✅ Active |
| **Profanity Filter (English)** | 40+ patterns | ✅ Active |
| **Profanity Filter (Urdu/Hindi)** | 50+ patterns | ✅ Active |
| **Violence/Hate Speech** | 15+ patterns | ✅ Active |
| **Off-Scope Query Handling** | Polite rejection | ✅ Active |

### API Security (v3.3.2)

| Endpoint | Protection | Access |
|----------|------------|--------|
| `/chat` | Session validation | Public |
| `/admin/status` | Rate limited | Public |
| `/admin/statistics` | Rate limited | Public |
| `/admin/groq-status` | Admin only | Restricted |
| `/admin/groq-toggle` | Admin only | Restricted |
| `/feedback/*` | Session validated | Public |

### Network Security

| Feature | Recommendation | Status |
|---------|----------------|--------|
| **HTTPS/TLS** | Required for production | ✅ Via Cloudflare |
| **CORS** | Restrict to trusted origins | ✅ Configurable |
| **Rate Limiting** | 100 requests/minute recommended | 🔧 Ready |
| **API Authentication** | JWT/API key for admin | 🔧 Ready |
| **Firewall** | Block unused ports | 🔧 Recommended |

---

## 🔐 LLM Security

### Groq API Protection (v3.3.2)

| Measure | Implementation |
|---------|----------------|
| **API Key Storage** | Environment variable only |
| **Toggle Control** | Admin-only endpoint |
| **Fallback Logic** | Graceful degradation |
| **Response Sanitization** | Same filters as local LLM |

### Answer Verification

| Layer | Protection |
|-------|------------|
| **Source Binding** | All answers from Manual only |
| **Citation Requirement** | Page reference mandatory |
| **Hallucination Prevention** | No external knowledge used |
| **Word Limit** | 100 words max per response |
| **Numeric Validation** | Values cross-checked |

---

## 🚨 Vulnerability Reporting

### How to Report

If you discover a security vulnerability in PDBOT:

1. **DO NOT** create a public GitHub issue
2. **Email** the developer directly (see contact below)
3. **Include** detailed information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact assessment
   - Suggested fixes (optional)

### Contact

**Developer:** M. Hassan Arif Afridi  
**LinkedIn:** [hassanarifafridi](https://www.linkedin.com/in/hassanarifafridi/)  
**GitHub:** [@athem135-source](https://github.com/athem135-source)

### Response Timeline

| Severity | Initial Response | Resolution Target |
|----------|------------------|-------------------|
| 🔴 Critical | 24 hours | 48 hours |
| 🟠 High | 48 hours | 1 week |
| 🟡 Medium | 1 week | 2 weeks |
| 🟢 Low | 2 weeks | 1 month |

---

## 📋 Deployment Security Checklist

### Pre-Deployment

- [ ] Enable HTTPS/TLS encryption
- [ ] Configure CORS to trusted domains only
- [ ] Set up rate limiting (100 req/min recommended)
- [ ] Enable API authentication for admin endpoints
- [ ] Review and update all dependencies
- [ ] Run security vulnerability scan
- [ ] Configure firewall rules (allow 5000, 3000, 6338)
- [ ] Set up monitoring and alerting
- [ ] Secure Groq API key in environment

### Post-Deployment

- [ ] Monitor access logs regularly
- [ ] Set up automated security scanning
- [ ] Keep dependencies updated weekly
- [ ] Review security policies quarterly
- [ ] Conduct periodic penetration testing
- [ ] Verify content filters effectiveness
- [ ] Test admin endpoint access controls

---

## ⚠️ Security Boundaries

### What PDBOT Protects Against

| Threat | Protection Level |
|--------|------------------|
| Prompt Injection | ✅ High - Strict RAG-only responses |
| Data Exfiltration | ✅ High - No external data access |
| Bribery/Corruption Queries | ✅ 100% - Hard-blocked |
| Inappropriate Content | ✅ High - 177+ filter patterns |
| Session Hijacking | ✅ Medium - Session isolation |
| DDoS | 🔧 Configurable - Rate limiting ready |

### Known Limitations

| Limitation | Mitigation |
|------------|------------|
| No authentication by default | Enable for production |
| Admin endpoints accessible | Add auth layer |
| Single document source | By design - focused scope |

---

## ⚖️ Disclaimer

```
THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.

The developer is not responsible for security breaches due to:
- Improper deployment or configuration
- Failure to implement recommended security measures
- Use in environments beyond intended scope
- Failure to update to latest versions

Users are responsible for:
- Properly configuring security settings
- Keeping the software updated
- Following security best practices
- Complying with applicable regulations
- Implementing network-level protections
```

---

<div align="center">

**Last Updated:** December 9, 2025  
**Version:** 3.3.2

*Security is a shared responsibility. Please report vulnerabilities responsibly.*

</div>
