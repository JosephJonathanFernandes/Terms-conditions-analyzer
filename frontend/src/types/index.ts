export type SourceType = "url" | "file" | "text";
export type DocumentStatus = "uploaded" | "extracted" | "failed";
export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type ExplanationLevel = "simple" | "standard" | "detailed";
export type LLMMode = "ai" | "rule-based";

export interface Document {
  id: number;
  filename: string;
  source_type: SourceType;
  source_url: string | null;
  content_hash: string | null;
  file_size: number | null;
  mime_type: string | null;
  status: DocumentStatus;
  uploaded_at: string;
  extracted_text: string | null;
}

export interface Clause {
  id: number;
  analysis_id: number;
  category: string;
  original_text: string;
  simplified_text: string | null;
  risk_level: RiskLevel;
  risk_rationale: string | null;
  confidence: number | null;
  source_location: string | null;
  paragraph_index: number | null;
  evidence: Record<string, unknown> | null;
  suggested_questions: string[] | null;
  created_at: string;
}

export interface Analysis {
  id: number;
  document_id: number;
  status: string;
  summary: string | null;
  risk_distribution: Record<string, number> | null;
  explanation_level: ExplanationLevel;
  llm_mode: LLMMode;
  created_at: string;
  clauses: Clause[];
}

export interface HistoryItem {
  id: number;
  document_id: number;
  filename: string;
  source_type: SourceType;
  status: DocumentStatus;
  created_at: string;
}

export interface Citation {
  clause_id: number;
  category: string;
  source_location: string | null;
  quote: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  document_does_not_specify: boolean;
}

export interface ClauseDiff {
  clause_id: number;
  category: string;
  change_type: "added" | "removed" | "modified";
  text_a: string | null;
  text_b: string | null;
  impact: string | null;
}

export interface ComparisonResponse {
  analysis_id_a: number;
  analysis_id_b: number;
  added: ClauseDiff[];
  removed: ClauseDiff[];
  modified: ClauseDiff[];
  impact_summary: string | null;
}

export interface IngestResponse {
  document_id: number | null;
  status: string;
  extracted_length: number;
  source_type: string;
  discovered_documents: Array<{ title: string; url: string; matched_keyword: string }> | null;
  message: string;
}

export interface DocumentListItem {
  id: number;
  filename: string;
  source_type: string;
  source_url: string | null;
  file_size: number | null;
  mime_type: string | null;
  status: string;
  failure_reason: string | null;
  page_count: number | null;
  uploaded_at: string | null;
  retention_delete_at: string | null;
  has_analysis: boolean;
}
