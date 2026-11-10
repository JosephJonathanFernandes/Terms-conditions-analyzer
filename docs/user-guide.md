# ClauseClear — User Guide

## What ClauseClear Does

ClauseClear helps you understand Terms & Conditions, Privacy Policies, and other legal documents before you accept them. It:

1. **Extracts** the actual legal text from a website URL, PDF, DOCX, or TXT file
2. **Detects** 21 types of legal clauses (data collection, payment terms, arbitration, etc.)
3. **Assesses risk** for each clause (LOW, MEDIUM, HIGH, CRITICAL)
4. **Simplifies** complex legal language into plain English
5. **Answers your questions** about the document with cited sources
6. **Compares** two versions of a document to show what changed
7. **Exports** a PDF report of the analysis

> ⚠️ **Important**: ClauseClear provides informational explanations only. This is **not legal advice**. Consult a qualified attorney for legal interpretation.

## Getting Started

### 1. Open the Application

Navigate to `http://localhost:5173` (or your deployed URL).

### 2. Choose an Input Method

You can analyze a document three ways:

| Method | Best For |
|--------|----------|
| **Website URL** | Terms & Conditions or Privacy Policy hosted online |
| **Upload Document** | PDF, DOCX, or TXT files you already have |
| **Paste Text** | Copy/paste text directly |

### 3. Start Analysis

After providing your document, click "Analyze" to extract and process the text.

### 4. Review Results

The results dashboard shows:

- **Executive Summary**: Plain-language overview
- **Risk Distribution**: How many clauses are LOW/MEDIUM/HIGH/CRITICAL
- **Clause Explorer**: Every detected clause with original text, simplified explanation, and risk level
- **Charts**: Visual breakdown of risk levels and clause categories

## Understanding Risk Levels

| Level | Meaning |
|-------|---------|
| **LOW** | Standard clause, minimal concern |
| **MEDIUM** | Notable terms worth reviewing |
| **HIGH** | Significant terms that may affect your rights |
| **CRITICAL** | Very concerning terms requiring close attention |

Risk levels are determined by the clause's wording, scope, exceptions, and context — not just by the category. Every risk assessment includes a rationale explaining why it was assigned.

## Ask Your Terms

Use the Q&A feature to ask specific questions:

- "Can they sell my data?"
- "Can I delete my account?"
- "Will my subscription renew automatically?"
- "Do I get a refund if I cancel?"

Answers are **grounded in the document** with citations to specific clauses. If the document doesn't specify something, ClauseClear will tell you.

## Compare Documents

Upload two versions of the same Terms & Conditions to see:
- **Added clauses** — new terms in the latest version
- **Removed clauses** — terms that were removed
- **Modified clauses** — terms that changed

## Export Reports

Download a PDF report containing:
- Executive summary
- Risk distribution
- All detected clauses with explanations
- Disclaimer (not legal advice)

## History & Document Management

- View all previous analyses
- Reopen any past analysis
- Export documents (TXT, JSON, PDF)
- Delete documents you no longer need

> Documents are subject to a retention policy. By default, uploaded documents are eligible for deletion after 30 days.

## Tips for Best Results

- **PDFs**: Text-based PDFs work best. Scanned/image-based PDFs may not extract correctly.
- **Websites**: Some sites block automated extraction or require JavaScript. If extraction fails, try pasting the text manually.
- **Long documents**: Very large documents are truncated to 200,000 characters for performance.
