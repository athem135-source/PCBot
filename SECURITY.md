# Security Policy

<div align="center">

![Security](https://img.shields.io/badge/Security-Policy-red?style=for-the-badge&logo=shield&logoColor=white)
![Version](https://img.shields.io/badge/Version-4.0.1-006600?style=for-the-badge)

**PCBot Security Guidelines & Vulnerability Reporting**

</div>

---

## 🛡️ Supported Versions

Only the current v4.0.x release line is supported. Older versions (v3.x and earlier) are archived and no longer receive security patches, bug fixes, or deployment support.

| Version | Status | Support Level |
|---------|--------|---------------|
| 4.0.1 | ✅ Current | Full support - security patches & features |
| 4.0.0 | ⚠️ Legacy | No active fixes; upgrade recommended |
| 3.x and earlier | ❌ Unsupported | Please upgrade to the latest v4.0.x release |

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

### API Security (v4.0.0)

| Endpoint | Protection | Access |
|----------|------------|--------|
| `/chat` | Session validation | Public |
| `/admin/authenticate` | Server-side password check | Public (login) |
| `/admin/run-stats` | Session-based auth | Admin only |
| `/admin/run-calibration` | Session-based auth | Admin only |
| `/admin/groq-status` | Rate limited | Public |
| `/admin/groq-toggle` | Admin only | Restricted |
| `/feedback/*` | Session validated | Public |

### Authentication & Access Control (v4.0.0)

| Feature | Implementation | Status |
|---------|----------------|--------|
| **Server-Side Auth** | Password validated via `/admin/authenticate` | ✅ Active |
| **Session Management** | Flask session cookies with httpOnly | ✅ Active |
| **Mode Separation** | User/Admin modes with different capabilities | ✅ Active |
| **No Client Secrets** | Zero passwords or keys in JavaScript | ✅ Active |
| **Virtual Env Isolation** | All packages in isolated .venv | ✅ Active |

### Network Security (v4.0.0)

| Feature | Implementation | Status |
|---------|----------------|--------|
| **HTTPS/TLS** | Required for production | ✅ Active |
| **GitHub Pages** | HTTPS by default, DDoS protection | ✅ Active |
| **Netlify** | CSP headers, X-Frame-Options, HSTS | ✅ Ready |
| **Cloudflare Tunnel** | Encrypted tunnels, temporary URLs | ✅ Active |
| **CORS** | Whitelist-based origin control | ✅ Configurable |
| **Rate Limiting** | 100 requests/minute recommended | 🔧 Ready |
| **API Authentication** | Session-based for admin endpoints | ✅ Active |
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
**Email:** hassanarifafridi@gmail.com  
**LinkedIn:** [Hassan Arif Afridi](https://www.linkedin.com/in/hassan-arif-afridi-150769363/)  
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

- [ ] Run `setup.bat` to create isolated virtual environment
- [ ] Enable HTTPS/TLS encryption (auto on GitHub Pages/Netlify)
- [ ] Configure CORS to trusted domains only
- [ ] Set up rate limiting (100 req/min recommended)
- [ ] Verify admin password is not default "nufc"
- [ ] Review and update all dependencies
- [ ] Run security vulnerability scan
- [ ] Configure firewall rules (allow ports: 5001, 6338, 11434)
- [ ] Set up monitoring and alerting
- [ ] Secure Groq API key in environment
- [ ] Test virtual environment isolation

### GitHub Pages Deployment

- [ ] Enable GitHub Actions deployment (Settings > Pages)
- [ ] Verify HTTPS is enforced
- [ ] Configure custom domain with SSL (optional)
- [ ] Review CORS settings for GitHub Pages URL
- [ ] Deploy backend separately (Railway, Render, etc.)
- [ ] Update API_BASE_URL in frontend HTML files

### Netlify Deployment

- [ ] Verify security headers in netlify.toml
- [ ] Enable HTTPS redirect
- [ ] Configure environment variables
- [ ] Set up backend deployment separately
- [ ] Test CORS configuration

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

| Limitation | Mitigation | v3.4.0 Status |
|------------|------------|---------------|
| Admin password in code | Change default password | 🔧 To-do |
| Session cookies | Use httpOnly, Secure flags | ✅ Implemented |
| Single document source | By design - focused scope | N/A |
| Virtual env dependency | Auto-created by setup.bat | ✅ Automated |

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

**Last Updated:** January 8, 2026  
**Version:** 3.4.0

*Security is a shared responsibility. Please report vulnerabilities responsibly.*

</div>
