import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { api } from "@/services/api";
import { riskColor, categoryLabel } from "@/utils/format";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/components/ui/toast";
import { Skeleton } from "@/components/ui/skeleton";
import { Copy } from "lucide-react";

export function ClauseDetail() {
  const { clauseId } = useParams<{ clauseId: string }>();
  const navigate = useNavigate();
  const [clause, setClause] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [related, setRelated] = useState<any[]>([]);

  useEffect(() => {
    if (!clauseId) return;
    loadClause();
  }, [clauseId]);

  const loadClause = async () => {
    try {
      const data = await api.getAnalysis(Number(clauseId));
      const c = data.clauses.find((cl: any) => cl.id === Number(clauseId));
      if (!c) {
        toast.error("Clause not found");
        return;
      }
      setClause(c);
      // Related clauses: same category, different clause
      setRelated(
        data.clauses.filter(
          (cl: any) => cl.category === c.category && cl.id !== Number(clauseId),
        ),
      );
    } catch (err: any) {
      toast.error(err.message || "Failed to load clause");
    } finally {
      setLoading(false);
    }
  };

  const copyText = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-20">
        <div className="bg-white rounded-xl border border-gray-200 p-8">
          <Skeleton variant="block" className="h-8 w-1/3 mb-3" />
          <Skeleton variant="block" className="h-6 w-full mb-3" />
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <Skeleton variant="block" className="h-24 w-full" />
            </div>
            <div className="space-y-4">
              <Skeleton variant="block" className="h-24 w-full" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!clause) {
    return (
      <div className="max-w-4xl mx-auto py-20 text-center">
        <p className="text-red-600">Clause not found.</p>
        <ButtonBack onClick={() => navigate(-1)} />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <button
        onClick={() => navigate(-1)}
        className="inline-flex items-center text-blue-600 text-sm hover:underline mb-4"
      >
        <span className="w-4 h-4 mr-2" aria-hidden="true">←</span> Back to analysis
      </button>

      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-bold text-navy-900">{categoryLabel(clause.category)}</h2>
            <p className="text-gray-600 text-sm">{clause.source_location || "No location reference"}</p>
          </div>
          <Badge variant="default" className={riskColor(clause.risk_level)}>
            {clause.risk_level}
          </Badge>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Original Text</h3>
              <button
                onClick={() => copyText(clause.original_text)}
                className="text-xs text-blue-600 hover:underline"
              >
                <Copy className="w-3 h-3 mr-1" /> Copy
              </button>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-100 text-sm text-gray-700 whitespace-pre-wrap font-mono">
              {clause.original_text}
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">Simplified Explanation</h3>
              <button
                onClick={() => copyText(clause.simplified_text || "")}
                className="text-xs text-blue-600 hover:underline"
              >
                <Copy className="w-3 h-3 mr-1" /> Copy
              </button>
            </div>
            <div className="bg-white rounded-lg p-4 border border-blue-100 text-sm text-gray-700 whitespace-pre-wrap">
              {clause.simplified_text || "No simplification available."}
            </div>
          </div>
        </div>

        {clause.risk_rationale && (
          <div className="mt-6 p-4 rounded-lg bg-amber-50 border border-amber-200">
            <h4 className="text-sm font-bold text-amber-800 mb-1">Why this risk level?</h4>
            <p className="text-amber-700 text-sm">{clause.risk_rationale}</p>
          </div>
        )}

        {clause.suggested_questions && clause.suggested_questions.length > 0 && (
          <div className="mt-6">
            <h4 className="text-sm font-bold text-navy-900 mb-2">Suggested questions</h4>
            <ul className="space-y-1 text-sm text-gray-600 list-disc list-inside">
              {clause.suggested_questions.map((q: string, i: number) => (
                <li key={i}>{q}</li>
              ))}
            </ul>
          </div>
        )}

        {related.length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h4 className="text-sm font-bold text-navy-900 mb-3">Related clauses ({related.length})</h4>
            <div className="space-y-3">
              {related.map((r) => (
                <div key={r.id} className="p-3 rounded-lg bg-gray-50 border border-gray-100">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-navy-900">{categoryLabel(r.category)}</span>
                    <span className={cn("text-xs font-medium border px-2 py-0.5 rounded", riskColor(r.risk_level))}>
                      {r.risk_level}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{r.original_text.slice(0, 150)}…</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ButtonBack({ onClick }: { onClick: () => void }) {
  return (
    <button onClick={onClick} className="text-sm text-blue-600 hover:underline">
      Back
    </button>
  );
}

function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}
