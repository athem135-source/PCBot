"""
Comparison Response Templates for PDBOT v2.5.0-patch4
Dynamic limits pulled from src/data/approval_limits.json (single source of truth).
"""

import json
import os
from typing import Optional, Dict

# Load approval limits from JSON to avoid hardcoding in code paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LIMITS_FILE = os.path.join(DATA_DIR, "approval_limits.json")

def _load_limits() -> Dict[str, Dict[str, str]]:
    try:
        with open(LIMITS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Fallback with empty dict; upstream should handle missing values
        return {}

LIMITS = _load_limits()

COMPARISON_RESPONSES = {
    "ddwp_cdwp_ecnec": f"""**Comparison: DDWP vs CDWP vs ECNEC**

| Aspect | DDWP | CDWP | ECNEC |
|--------|------|------|-------|
| **Full Name** | {LIMITS.get('DDWP', {}).get('full_name', 'Divisional Development Working Party')} | {LIMITS.get('CDWP', {}).get('full_name', 'Central Development Working Party')} | {LIMITS.get('ECNEC', {}).get('full_name', 'Executive Committee of the National Economic Council')} |
| **Level** | Divisional/Provincial | Federal | National |
| **Approval Limit** | {LIMITS.get('DDWP', {}).get('limit_text', '')} | {LIMITS.get('CDWP', {}).get('limit_text', '')} | {LIMITS.get('ECNEC', {}).get('limit_text', '')} |
| **Chair** | Commissioner/Additional Chief Secretary | Deputy Chairman Planning Commission | Prime Minister/Finance Minister |
| **Scope** | Provincial/Divisional projects | Federal/large provincial projects | Mega/strategic national projects |

**Key Difference:** Approval authority depends on project cost thresholds.""",

    "ddwp_cdwp": f"""**Comparison: DDWP vs CDWP**

| Aspect | DDWP | CDWP |
|--------|------|------|
| **Full Name** | {LIMITS.get('DDWP', {}).get('full_name', 'Divisional Development Working Party')} | {LIMITS.get('CDWP', {}).get('full_name', 'Central Development Working Party')} |
| **Level** | Divisional/Provincial | Federal |
| **Approval Limit** | {LIMITS.get('DDWP', {}).get('limit_text', '')} | {LIMITS.get('CDWP', {}).get('limit_text', '')} |

**Key Difference:** DDWP approves smaller provincial projects; CDWP approves larger federal/provincial projects in scope.""",

    "cdwp_ecnec": f"""**Comparison: CDWP vs ECNEC**

| Aspect | CDWP | ECNEC |
|--------|------|-------|
| **Full Name** | {LIMITS.get('CDWP', {}).get('full_name', 'Central Development Working Party')} | {LIMITS.get('ECNEC', {}).get('full_name', 'Executive Committee of the National Economic Council')} |
| **Approval Limit** | {LIMITS.get('CDWP', {}).get('limit_text', '')} | {LIMITS.get('ECNEC', {}).get('limit_text', '')} |
| **Chair** | Deputy Chairman Planning Commission | Prime Minister/Finance Minister |

**Key Difference:** ECNEC is the highest approval authority; projects above the CDWP ceiling require ECNEC approval.""",

    "pc_forms": """**Comparison: PC Proformas**

| Form | Purpose | When Used |
|------|---------|-----------|
| **PC-I** | Project Proposal | New project approval request |
| **PC-II** | Feasibility Study | Pre-investment studies |
| **PC-III** | Progress Report | Quarterly/annual monitoring |
| **PC-IV** | Completion Report | Project completion |
| **PC-V** | Annual Re-appropriation | Budget revision |

**Key Difference:** PC-I starts the project, PC-III monitors it, PC-IV closes it.""",

    "federal_provincial": """**Comparison: Federal vs Provincial Project Approval**

| Aspect | Federal Projects | Provincial Projects |
|--------|-----------------|---------------------|
| **Funding Source** | PSDP | ADP |
| **Approval Authority** | CDWP/ECNEC | PDWP/DDWP |
| **Oversight** | Planning Commission | Provincial P&D |

**Key Difference:** Federal projects use PSDP funding and go through CDWP/ECNEC."""
}



# v2.5.0-patch3: Approval Limits Table (for numeric queries)
APPROVAL_LIMITS_TABLE = f'''**Project Approval Limits by Forum**

| Forum | Full Name | Approval Limit |
|-------|-----------|----------------|
| **DDWP** | {LIMITS.get('DDWP', {}).get('full_name', 'Divisional Development Working Party')} | {LIMITS.get('DDWP', {}).get('limit_text', '')} |
| **PDWP** | {LIMITS.get('PDWP', {}).get('full_name', 'Provincial Development Working Party')} | {LIMITS.get('PDWP', {}).get('limit_text', '')} |
| **CDWP** | {LIMITS.get('CDWP', {}).get('full_name', 'Central Development Working Party')} | {LIMITS.get('CDWP', {}).get('limit_text', '')} |
| **ECNEC** | {LIMITS.get('ECNEC', {}).get('full_name', 'Executive Committee of the National Economic Council')} | {LIMITS.get('ECNEC', {}).get('limit_text', '')} |

**Notes:**
- Projects within provincial limits go to PDWP/DDWP
- Federal projects between Rs. 2-10 billion go to CDWP
- Mega projects above Rs. 10 billion require ECNEC approval

*Source: Manual for Development Projects 2024*'''
def get_comparison_response(query):
    """Check if query matches a known comparison or limit query."""
    q_lower = query.lower()

    # v2.5.0-patch4: Specific forum limit queries first (single forum only)
    limit_terms = ['limit', 'approval', 'threshold', 'cap', 'ceiling']
    mentions = {f: (f.lower() in q_lower) for f in ['ddwp', 'pdwp', 'cdwp', 'ecnec']}
    if any(t in q_lower for t in limit_terms):
        count = sum(1 for k, v in mentions.items() if v)
        if count == 1:
            if mentions['ddwp']:
                return f"**DDWP Approval Limit**\n\n{LIMITS.get('DDWP', {}).get('limit_text', '')}"
            if mentions['pdwp']:
                return f"**PDWP Approval Limit**\n\n{LIMITS.get('PDWP', {}).get('limit_text', '')}"
            if mentions['cdwp']:
                return f"**CDWP Approval Limit**\n\n{LIMITS.get('CDWP', {}).get('limit_text', '')}"
            if mentions['ecnec']:
                return f"**ECNEC Approval Limit**\n\n{LIMITS.get('ECNEC', {}).get('limit_text', '')}"
        elif count >= 2 or 'all' in q_lower:
            return APPROVAL_LIMITS_TABLE

    
    if all(term in q_lower for term in ["ddwp", "cdwp", "ecnec"]):
        return COMPARISON_RESPONSES["ddwp_cdwp_ecnec"]
    
    if "ddwp" in q_lower and "cdwp" in q_lower:
        return COMPARISON_RESPONSES["ddwp_cdwp"]
    
    if "cdwp" in q_lower and "ecnec" in q_lower:
        return COMPARISON_RESPONSES["cdwp_ecnec"]
    
    pc_terms = ["pc-i", "pc-ii", "pc-iii", "pc-iv", "pc-v"]
    pc_matches = sum(1 for term in pc_terms if term in q_lower)
    if pc_matches >= 2 or ("pc" in q_lower and "difference" in q_lower):
        return COMPARISON_RESPONSES["pc_forms"]
    
    if ("federal" in q_lower and "provincial" in q_lower):
        return COMPARISON_RESPONSES["federal_provincial"]
    
    entities = []
    if "ddwp" in q_lower: entities.append("ddwp")
    if "cdwp" in q_lower: entities.append("cdwp")
    if "ecnec" in q_lower: entities.append("ecnec")
    
    if len(entities) >= 3:
        return COMPARISON_RESPONSES["ddwp_cdwp_ecnec"]
    elif len(entities) == 2:
        key = "_".join(sorted(entities))
        return COMPARISON_RESPONSES.get(key)
    
    return None
