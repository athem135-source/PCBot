import re
from typing import List, Tuple, Dict, Any

# Prefer the modern langchain text splitters package; fall back to classic import; else None
try:  # langchain-text-splitters (recommended)
    from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
except Exception:  # classic langchain fallback
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
    except Exception:
        RecursiveCharacterTextSplitter = None  # type: ignore


def clean_text(text: str) -> str:
    """Sanitize user input by removing unwanted characters and excess whitespace."""
    if text is None:
        return ""
    # normalize line endings and collapse whitespace
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return ' '.join(text.split())


def format_response(response: str) -> str:
    """Format the chatbot's response for better readability."""
    return response.strip() if response else "I'm sorry, I didn't understand that."


def chunk_text(text: str, max_chars: int = 1200) -> List[str]:
    """
    Split text into overlapping character windows.

    FIX-1: increase chunk size and add overlap
    - We use a sliding window with ~300 character overlap to preserve cross-boundary
      context (e.g., PC-I through PC-V spans).
    - Signature unchanged; callers can pass a different max_chars. We recommend 1900.
    """
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return []

    overlap = 300
    size = max(200, max_chars)
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + size)
        chunk = text[start:end]
        # try to snap to a boundary for readability
        if end < n:
            tail = chunk[-120:]
            m = re.search(r"[\.!?\n]\s*\Z", tail)
            if m:
                end = start + len(chunk) - (len(tail) - m.start())
                chunk = text[start:end]
        chunks.append(chunk.strip())
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks


def chunk_text_sentences(text: str, target_chars: int = 800, chunk_overlap: int = 120) -> List[str]:
    """
    Split text into sentence-aware chunks using LangChain's RecursiveCharacterTextSplitter when available.

    - Targets ~`target_chars` per chunk and overlaps by `chunk_overlap`.
    - Uses sentence and newline boundaries as preferred split points for better retrieval accuracy.
    - Falls back to a simple sentence grouper if LangChain is not installed.
    """
    raw = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not raw:
        return []

    # Preferred: LangChain splitter with sentence-aware separators
    if RecursiveCharacterTextSplitter is not None:
        # Order from strongest to weakest boundary; keeps punctuation attached to sentence
        separators = [
            "\n\n",  # paragraphs
            "\n",    # lines
            ". ",    # sentence
            "? ",
            "! ",
            "; ",    # clause (optional)
            ", ",    # soft
            " ",     # spaces
            ""       # any
        ]
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=max(200, int(target_chars)),
            chunk_overlap=max(0, int(chunk_overlap)),
            length_function=len,
            separators=separators,
        )
        chunks = [c.strip() for c in splitter.split_text(raw) if c and c.strip()]
        return chunks

    # Fallback: naive sentence split + greedy grouping near target length
    sentences = split_into_sentences(raw)
    if not sentences:
        return [raw]
    out: List[str] = []
    buf: List[str] = []
    cur = 0
    for s in sentences:
        s2 = s.strip()
        if not s2:
            continue
        if cur + len(s2) + (1 if buf else 0) <= target_chars:
            buf.append(s2)
            cur += len(s2) + (1 if buf[:-1] else 0)
        else:
            if buf:
                out.append(" ".join(buf).strip())
            # start new buffer; add overlap by carrying last sentence if small
            if out and chunk_overlap > 0 and out[-1]:
                last = out[-1]
                # take a tail slice of the last chunk to simulate overlap context
                tail = last[max(0, len(last) - chunk_overlap):]
                buf = [tail, s2]
                cur = len(tail) + 1 + len(s2)
            else:
                buf = [s2]
                cur = len(s2)
    if buf:
        out.append(" ".join(buf).strip())
    # Final tidy
    return [c for c in out if c]


def _score_relevance(query: str, chunk: str, exact_phrase: bool = False) -> float:
    """Simple relevance score with optional exact-phrase and abbreviation boosts."""
    q = (query or "").strip()
    c = (chunk or "")
    qtoks = re.findall(r"\w+", q.lower())
    ctoks = re.findall(r"\w+", c.lower())
    if not qtoks or not ctoks:
        return 0.0
    qset = set(qtoks)
    cset = set(ctoks)
    overlap = len(qset & cset)
    uniq = len(cset)
    base = overlap * 3 + min(uniq / 50.0, 2.0)

    # FIX-5: Boost when the question mentions PC-I..PC-V or common bodies (ECNEC, CDWP)
    qn = re.sub(r"[\u2012-\u2015]", "-", q.lower())
    cn = re.sub(r"[\u2012-\u2015]", "-", c.lower())
    key_patterns = [r"\bpc-?[ivx]+\b", r"\becnec\b", r"\bcdwp\b", r"\bddwp\b"]
    for pat in key_patterns:
        if re.search(pat, qn) and re.search(pat, cn):
            base += 6.0

    if exact_phrase:
        qnorm = re.sub(r"\s+", " ", q.lower())
        cnorm = re.sub(r"\s+", " ", c.lower())
        idx = cnorm.find(qnorm) if qnorm else -1
        if idx >= 0:
            count = cnorm.count(qnorm)
            pos_bonus = 2.0 if idx < 100 else 1.0
            base += 10.0 + (count - 1) * 1.0 + pos_bonus
    return base


def select_relevant_chunks(query: str, chunks: List[str], top_k: int = 3, exact_phrase: bool = False) -> List[Tuple[float, str]]:
    """
    Rank chunks by relevance; include adjacency for PC-* queries and a fallback
    simplified query when initial scoring is weak.

    FIX-6: Deduplicate identical chunk text in the final selection.
    FIX-7: Fallback search with simplified query (keep uppercase, hyphenated, >=3 chars).
    """
    chunks = chunks or []

    def _score_all(q: str) -> List[Tuple[float, int, str]]:
        arr: List[Tuple[float, int, str]] = []
        for i, c in enumerate(chunks):
            arr.append((_score_relevance(q, c, exact_phrase=exact_phrase), i, c))
        arr.sort(key=lambda x: x[0], reverse=True)
        return arr

    scored = _score_all(query)
    if not scored or scored[0][0] <= 0.0:
        toks = re.findall(r"[A-Za-z0-9\-]+", (query or ""))
        keep = [t for t in toks if (t.isupper() or '-' in t or len(t) >= 3)]
        simp = " ".join(keep) if keep else (query or "")
        scored = _score_all(simp)

    q_has_pc = bool(re.search(r"\bpc[-\u2012-\u2015]?[ivx]+\b", (query or "").lower()))
    chosen: List[Tuple[float, int, str]] = []
    seen_idx = set()
    for sc, idx, ch in scored:
        if len(chosen) >= top_k:
            break
        chosen.append((sc, idx, ch))
        seen_idx.add(idx)
        if q_has_pc:
            for j in (idx - 1, idx + 1):
                if 0 <= j < len(chunks) and j not in seen_idx:
                    chosen.append((sc * 0.8, j, chunks[j]))
                    seen_idx.add(j)
                    if len(chosen) >= top_k:
                        break

    out: List[Tuple[float, str]] = []
    seen_text = set()
    for sc, _, ch in sorted(chosen, key=lambda x: x[0], reverse=True):
        if len(out) >= top_k:
            break
        key = ch.strip()
        if key in seen_text:
            continue
        seen_text.add(key)
        out.append((sc, ch))

    if not out:
        out = [(sc, ch) for sc, _, ch in scored[: max(1, min(top_k, len(scored)))]]
    return out


def highlight_matches(text: str, query: str) -> str:
    """Return HTML with case-insensitive exact substring matches highlighted using <mark>."""
    if not text:
        return ""
    q = (query or "").strip()
    if not q:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _escape(s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    escaped = _escape(text)
    q_escaped = _escape(q)
    q_escaped_norm = re.sub(r"\s+", " ", q_escaped)
    try:
        pattern = re.compile(re.escape(q_escaped_norm), re.IGNORECASE)
    except re.error:
        pattern = None
    if pattern and q_escaped_norm:
        return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", escaped)
    return escaped


def split_into_sentences(text: str) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


# =============================================================================
# PRECISION CHUNKING v3.3.0 - For Munawar Test Optimization
# =============================================================================

# Noise patterns to remove during chunking
NOISE_PATTERNS = [
    r"^(Page\s+)?\d+(\s+of\s+\d+)?$",  # Page numbers
    r"^Manual for Development Projects",  # Headers
    r"^Planning Commission",  # Headers
    r"^(Table|Figure|Annexure|Appendix)\s+[\d\w\-]+",  # Table/figure titles
    r"^[\d\s\.,\-\(\)]+$",  # Numeric-only garbage
    r"^Chapter\s+\d+",  # Chapter headers
    r"^Section\s+\d+",  # Section headers
    r"^\d+\.\d+(\.\d+)?\s*$",  # Section numbers only
]


def clean_chunk_text(text: str) -> str:
    """
    Clean text for chunking: remove headers, page numbers, table titles, noise.
    v3.3.0: Stricter cleaning for precision retrieval.
    """
    if not text:
        return ""
    
    lines = text.split("\n")
    cleaned = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Skip noise patterns
        skip = False
        for pattern in NOISE_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                skip = True
                break
        
        if skip:
            continue
        
        # Skip very short lines (likely labels/numbers)
        if len(line) < 10 and not any(c.isalpha() for c in line):
            continue
        
        cleaned.append(line)
    
    result = " ".join(cleaned)
    # Normalize whitespace
    result = re.sub(r"\s+", " ", result).strip()
    return result


def chunk_precision_sentences(
    text: str,
    min_words: int = 12,
    max_words: int = 70,
    neighbor_context: int = 1
) -> List[str]:
    """
    v3.3.0 Precision Chunking for Munawar Test optimization.
    
    Creates tight 1-3 sentence chunks with:
    - Max 70 words per chunk (default)
    - Min 12 words to avoid garbage
    - ±1 neighbor sentence for context (same topic only)
    - Removal of all noise (headers, page numbers, table titles)
    
    Args:
        text: Raw text to chunk
        min_words: Minimum words per chunk (filter short garbage)
        max_words: Maximum words per chunk (prevents over-context)
        neighbor_context: How many neighbor sentences to include (0-1)
    
    Returns:
        List of precision chunks
    """
    # Step 1: Clean the text
    cleaned = clean_chunk_text(text)
    if not cleaned or len(cleaned) < 20:
        return []
    
    # Step 2: Split into sentences
    sentences = split_into_sentences(cleaned)
    if not sentences:
        return []
    
    # Step 3: Build precision chunks (1-3 sentences, max 70 words)
    chunks = []
    i = 0
    
    while i < len(sentences):
        buffer = []
        word_count = 0
        
        # Add current sentence
        current = sentences[i].strip()
        if not current:
            i += 1
            continue
        
        current_words = len(current.split())
        buffer.append(current)
        word_count = current_words
        
        # Try to add next sentence if under word limit and same topic
        if i + 1 < len(sentences) and neighbor_context > 0:
            next_sent = sentences[i + 1].strip()
            next_words = len(next_sent.split())
            
            # Only add if: (1) under word limit, (2) not too long itself
            if word_count + next_words <= max_words and next_words <= 50:
                # Check topic continuity (shared keywords)
                if _same_topic(current, next_sent):
                    buffer.append(next_sent)
                    word_count += next_words
                    i += 1  # Skip next sentence since we included it
        
        # Create chunk
        chunk_text = " ".join(buffer).strip()
        chunk_word_count = len(chunk_text.split())
        
        # Only add if meets minimum word count
        if chunk_word_count >= min_words:
            chunks.append(chunk_text)
        
        i += 1
    
    return chunks


def _same_topic(sent1: str, sent2: str) -> bool:
    """
    Check if two sentences are on the same topic.
    Uses keyword overlap to determine continuity.
    """
    # Extract significant words (length >= 4, not common)
    stopwords = {"this", "that", "with", "from", "have", "been", "will", "shall", "would", "could", "should", "their", "which", "where", "when", "what", "these", "those"}
    
    def get_keywords(text):
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        return set(w for w in words if w not in stopwords)
    
    kw1 = get_keywords(sent1)
    kw2 = get_keywords(sent2)
    
    if not kw1 or not kw2:
        return False
    
    # Overlap ratio
    overlap = len(kw1 & kw2)
    min_len = min(len(kw1), len(kw2))
    
    # At least 20% overlap or 2+ shared keywords
    return overlap >= 2 or (min_len > 0 and overlap / min_len >= 0.2)


def trim_answer_to_limit(answer: str, max_words: int = 70) -> str:
    """
    Trim answer to word limit, preserving sentence boundaries.
    v3.3.0: For answer composer post-processing.
    
    Args:
        answer: Raw answer text
        max_words: Maximum words allowed (default 70)
    
    Returns:
        Trimmed answer ending at sentence boundary
    """
    if not answer:
        return ""
    
    words = answer.split()
    if len(words) <= max_words:
        return answer
    
    # Take first max_words words
    truncated = " ".join(words[:max_words])
    
    # Try to end at sentence boundary
    last_period = truncated.rfind(".")
    last_question = truncated.rfind("?")
    last_exclaim = truncated.rfind("!")
    
    last_boundary = max(last_period, last_question, last_exclaim)
    
    if last_boundary > len(truncated) * 0.5:  # At least halfway through
        return truncated[:last_boundary + 1].strip()
    
    # No good boundary, just add period
    return truncated.rstrip(".!?,;") + "."


def format_single_citation(page: int, doc_name: str = "Manual for Development Projects 2024") -> str:
    """
    Format a single, clean citation.
    v3.3.0: Ensures consistent citation format.
    
    Args:
        page: Page number
        doc_name: Document title
    
    Returns:
        Formatted citation string: "Source: Manual 2024, p.XX"
    """
    if page and page > 0:
        return f"Source: {doc_name}, p.{page}"
    return f"Source: {doc_name}"


def extract_exact_quotes(query: str, chunks: List[str], max_quotes: int = 5) -> List[str]:
    """Return sentences that contain the exact (case-insensitive) query substring."""
    q = (query or "").strip().lower()
    if not q:
        return []
    quotes: List[str] = []
    seen = set()
    for ch in chunks or []:
        for sent in split_into_sentences(ch):
            s_norm = re.sub(r"\s+", " ", sent.strip().lower())
            if q in s_norm and sent not in seen:
                quotes.append(sent.strip())
                seen.add(sent)
                if len(quotes) >= max_quotes:
                    return quotes
    return quotes


def find_exact_locations(query: str, pages: List[str], max_results: int = 10) -> List[Dict[str, Any]]:
    """Find exact (case-insensitive) occurrences of query in page texts and return metadata.

    Returns list of dicts with keys: page (1-based), paragraph (1-based), line (1-based), sentence (str).
    """
    q = (query or "").strip()
    if not q:
        return []
    qnorm = re.sub(r"\s+", " ", q.lower())
    results: List[Dict[str, Any]] = []

    for p_idx, page in enumerate(pages or [], start=1):
        # Keep original newlines for paragraph/line computation
        page_text = page or ""
        # Compute paragraphs and lines
        paragraphs = [pp for pp in re.split(r"\n{2,}", page_text) if pp.strip()]
        lines = [ln for ln in re.split(r"\n+", page_text) if ln.strip()]

        # Sentences for quote extraction
        sentences = split_into_sentences(page_text)
        for sent in sentences:
            snorm = re.sub(r"\s+", " ", sent.lower())
            if qnorm and qnorm in snorm:
                # paragraph index: first paragraph that contains the sentence substring
                para_num = 1
                for i, pp in enumerate(paragraphs, start=1):
                    if sent in pp:
                        para_num = i
                        break
                # line index: first line where the query appears
                line_num = 1
                qpos_line = -1
                for i, ln in enumerate(lines, start=1):
                    if qnorm in re.sub(r"\s+", " ", ln.lower()):
                        qpos_line = i
                        break
                if qpos_line != -1:
                    line_num = qpos_line
                results.append({
                    "page": p_idx,
                    "paragraph": para_num,
                    "line": line_num,
                    "sentence": sent.strip(),
                })
                if len(results) >= max_results:
                    return results
    return results


def extract_factual_items(query: str, chunks: List[str], max_items: int = 5) -> List[str]:
    """Heuristic factual extraction: select sentences near the query that contain numbers, dates, or definition cues."""
    qtokens = set(re.findall(r"\w+", (query or "").lower()))
    if not qtokens:
        return []
    candidates: List[Tuple[float, str]] = []
    num_re = re.compile(r"\b\d{1,4}(?:[.,]\d+)?\b")
    date_re = re.compile(r"\b(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{1,2}-\d{1,2}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b", re.I)
    def_re = re.compile(r"\b(is|means|refers to)\b|:", re.I)

    def score_sentence(s: str) -> float:
        stoks = set(re.findall(r"\w+", s.lower()))
        overlap = len(stoks & qtokens)
        has_num = 1 if num_re.search(s) else 0
        has_date = 1 if date_re.search(s) else 0
        has_def = 1 if def_re.search(s) else 0
        return overlap * 3 + has_def * 2 + has_num * 1.5 + has_date * 1.0

    for ch in chunks or []:
        for sent in split_into_sentences(ch):
            sc = score_sentence(sent)
            if sc > 0:
                candidates.append((sc, sent.strip()))
    candidates.sort(key=lambda x: x[0], reverse=True)
    # Deduplicate while preserving order
    out: List[str] = []
    seen = set()
    for _, s in candidates:
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
        if len(out) >= max_items:
            break
    return out


# --- Generative helpers ---
def render_citations(citations: List[Dict[str, Any]], manual_title: str = "Manual for Development Projects 2024") -> str:
    """Render a Sources block in the proper format (v1.8.0 fix).
    
    Format:
    Source: Manual for Development Projects 2024, p.XX
    
    NEVER outputs:
    - [5] or bracketed numbers
    - Page N/A or placeholder values
    - Multiple entries (just first 1-3 sources)
    
    Args:
        citations: List of citation dicts with 'page' key
        manual_title: Title of the manual
    
    Returns:
        Formatted citation string
    """
    if not citations:
        return ""
    
    # Take only first valid citation (single source format)
    first_valid = None
    for c in citations:
        page = c.get("page")
        if page and str(page).replace(".", "").replace(",", "").isdigit():
            first_valid = c
            break

    if not first_valid:
        return ""

    page = first_valid.get("page", "?")
    return f"\n\nSource: {manual_title}, p.{page}"


def to_markdown_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Return a GitHub-flavored Markdown table string.

    headers: ["Col1", "Col2", ...]
    rows: [[v11, v12, ...], [v21, v22, ...], ...]
    """
    if not headers:
        return ""
    hline = "| " + " | ".join(str(h) for h in headers) + " |"
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    blines = [hline, sep]
    for r in rows or []:
        vals = [str(v) for v in r]
        # Pad or trim row to header width
        if len(vals) < len(headers):
            vals += [""] * (len(headers) - len(vals))
        elif len(vals) > len(headers):
            vals = vals[: len(headers)]
        blines.append("| " + " | ".join(vals) + " |")
    return "\n".join(blines)

