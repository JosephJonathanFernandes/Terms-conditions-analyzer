"""Retrieval-Augmented Generation service.

Uses TF-IDF-based retrieval over document clauses (sentence-transformers
optional). Returns grounded answers with citations to source clauses.
"""

import re
import math
from typing import List, Dict, Any, Tuple
from collections import Counter

from app.services.simplification_service import simplify
from app.services.llm_provider import get_provider


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


class TfidfRetriever:
    def __init__(self, clauses: List[dict]):
        self.clauses = clauses
        self.docs = [_tokenize(c.get("original_text", "")) for c in clauses]
        self.df: Dict[str, int] = Counter()
        for doc in self.docs:
            for term in set(doc):
                self.df[term] += 1
        self.n = len(self.docs)

    def _tfidf(self, doc: List[str]) -> Dict[str, float]:
        tf = Counter(doc)
        total = len(doc) or 1
        return {
            term: (count / total) * math.log((self.n + 1) / (self.df.get(term, 0) + 1)) + 1
            for term, count in tf.items()
        }

    def retrieve(self, question: str, top_k: int = 5) -> List[Tuple[dict, float]]:
        q_terms = _tokenize(question)
        if not q_terms or self.n == 0:
            return []
        q_vec = Counter(q_terms)
        scores = []
        for i, doc in enumerate(self.docs):
            d_vec = self._tfidf(doc)
            dot = sum(q_vec.get(t, 0) * d_vec.get(t, 0) for t in q_terms)
            q_norm = math.sqrt(sum(v * v for v in q_vec.values())) or 1
            d_norm = math.sqrt(sum(v * v for v in d_vec.values())) or 1
            score = dot / (q_norm * d_norm)
            if score > 0:
                scores.append((score, i))
        scores.sort(reverse=True)
        return [(self.clauses[i], score) for score, i in scores[:top_k]]


def answer_question(question: str, clauses: List[dict]) -> dict:
    """Generate a grounded answer with citations. If info absent, say so."""
    retriever = TfidfRetriever(clauses)
    top = retriever.retrieve(question, top_k=5)

    if not top:
        return {
            "answer": "The document does not specify this information.",
            "citations": [],
            "document_does_not_specify": True,
        }

    # Build context from top clauses.
    context_parts = []
    citations = []
    for clause, score in top:
        context_parts.append(
            f"[{clause['id']}] ({clause['category']}) {clause['original_text']}"
        )
        citations.append({
            "clause_id": clause["id"],
            "category": clause["category"],
            "source_location": clause.get("source_location"),
            "quote": clause["original_text"][:300],
        })

    context = "\n\n".join(context_parts)

    provider = get_provider()
    if provider.is_available():
        result = provider.answer_question(question, context)
        answer = result.get("answer", "")
        # Ensure citations from retrieval are attached.
        if not result.get("citations"):
            result["citations"] = citations
        result["document_does_not_specify"] = _is_absent(answer)
        return result

    # Rule-based fallback: answer from retrieved clauses.
    answer = _rule_based_answer(question, top)
    return {
        "answer": answer,
        "citations": citations,
        "document_does_not_specify": _is_absent(answer),
    }


def _rule_based_answer(question: str, top: List[Tuple[dict, float]]) -> str:
    if not top:
        return "The document does not specify this information."
    best = top[0][0]
    text = best.get("original_text", "")
    return (
        f"Based on the document, this appears related to '{best['category']}': "
        f"{text[:500]} "
        "(Rule-based answer — no LLM configured.)"
    )


def _is_absent(answer: str) -> bool:
    absent_phrases = [
        "does not specify",
        "not mentioned",
        "no information",
        "not specified",
        "document does not",
    ]
    lower = answer.lower()
    return any(p in lower for p in absent_phrases)


def simplify_clause(clause: dict, level: str = "standard") -> dict:
    return simplify(
        clause.get("original_text", ""),
        clause.get("category", ""),
        level,
        context=clause.get("risk_rationale", ""),
    )
