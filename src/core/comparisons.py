"""
Comparison Response Templates for PDBOT v3.3.1
NO HARDCODED LIMITS - All numeric values come from RAG (the actual manual).
Only structural comparisons (PC forms, federal vs provincial) use templates.
Limit queries return None to let RAG fetch from the manual.
"""

from typing import Optional


# =============================================================================
# STRUCTURAL COMPARISONS ONLY (no numeric values)
# =============================================================================

COMPARISON_RESPONSES = {
    "pc_forms": """**Comparison: PC Proformas**

| Form | Purpose | When Used |
|------|---------|-----------|
| **PC-I** | Project Proposal | New project approval request |
| **PC-II** | Feasibility Study | Pre-investment studies |
| **PC-III** | Progress Report | Quarterly/annual monitoring |
| **PC-IV** | Completion Report | Project completion |
| **PC-V** | Annual Re-appropriation | Budget revision |

**Key Difference:** PC-I starts the project, PC-III monitors it, PC-IV closes it.

*Source: Manual for Development Projects 2024*""",

    "federal_provincial": """**Comparison: Federal vs Provincial Project Approval**

| Aspect | Federal Projects | Provincial Projects |
|--------|-----------------|---------------------|
| **Funding Source** | PSDP | ADP |
| **Approval Authority** | CDWP/ECNEC | PDWP/DDWP |
| **Oversight** | Planning Commission | Provincial P&D |

**Key Difference:** Federal projects use PSDP funding and go through CDWP/ECNEC.

*Source: Manual for Development Projects 2024*"""
}


def get_comparison_response(query: str) -> Optional[str]:
    """
    v3.3.1: Check if query matches a known STRUCTURAL comparison.
    
    IMPORTANT: This function NO LONGER handles limit/threshold queries.
    All numeric queries (DDWP limit, CDWP threshold, etc.) return None
    so that the RAG pipeline fetches the actual values from the manual.
    
    Only handles:
    - PC form comparisons (PC-I vs PC-II, etc.)
    - Federal vs Provincial structure
    
    Returns:
        Template response for structural comparisons, or None for RAG.
    """
    q_lower = query.lower()
    
    # ==========================================================
    # LIMIT/THRESHOLD QUERIES -> Return None, let RAG handle
    # ==========================================================
    limit_terms = ['limit', 'approval limit', 'threshold', 'cap', 'ceiling', 
                   'how much', 'maximum', 'max', 'can approve', 'approval power']
    forum_terms = ['ddwp', 'pdwp', 'cdwp', 'ecnec', 'nec']
    
    # If query mentions limits AND forums, let RAG handle it
    has_limit_term = any(t in q_lower for t in limit_terms)
    has_forum_term = any(t in q_lower for t in forum_terms)
    
    if has_limit_term and has_forum_term:
        # Return None - RAG will fetch actual values from manual
        return None
    
    # ==========================================================
    # FORUM COMPARISONS (difference between X and Y) -> Return None
    # Let RAG provide accurate comparison from manual
    # ==========================================================
    comparison_terms = ['difference', 'differ', 'compare', 'vs', 'versus', 'between']
    has_comparison = any(t in q_lower for t in comparison_terms)
    
    if has_comparison and has_forum_term:
        # Return None - RAG will fetch actual comparison from manual
        return None
    
    # ==========================================================
    # PC FORMS COMPARISON -> Use template (structural, not numeric)
    # ==========================================================
    pc_terms = ["pc-i", "pc-ii", "pc-iii", "pc-iv", "pc-v", "pc1", "pc2", "pc3", "pc4", "pc5"]
    pc_matches = sum(1 for term in pc_terms if term in q_lower.replace(" ", ""))
    
    if pc_matches >= 2:
        return COMPARISON_RESPONSES["pc_forms"]
    
    if "pc" in q_lower and has_comparison:
        return COMPARISON_RESPONSES["pc_forms"]
    
    # ==========================================================
    # FEDERAL VS PROVINCIAL -> Use template (structural)
    # ==========================================================
    if "federal" in q_lower and "provincial" in q_lower:
        return COMPARISON_RESPONSES["federal_provincial"]
    
    if ("psdp" in q_lower and "adp" in q_lower):
        return COMPARISON_RESPONSES["federal_provincial"]
    
    # ==========================================================
    # DEFAULT: Return None, let RAG handle
    # ==========================================================
    return None
