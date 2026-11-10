import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "@/services/api";
import { formatDate } from "@/utils/format";
import { Loader2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/toast";

export function AnalysisPage() {
  const { documentId } = useParams<{ documentId: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!documentId) return;
    loadAnalysis();
  }, [documentId]);

  const loadAnalysis = async () => {
    try {
      const data = await api.getAnalysis(Number(documentId));
      setAnalysis(data);
    } catch (err: any) {
      setError(err.message || "Failed to load analysis");
      toast.error(err.message || "Failed to load analysis");
    } finally {
      setLoading(false);
    }
  };

  const startAnalysis = async () => {
    if (!documentId) return;
    setLoading(true);
    try {
      const data = await api.analyze(Number(documentId));
      setAnalysis(data);
      toast.success("Analysis complete");
    } catch (err: any) {
      setError(err.message || "Analysis failed");
      toast.error(err.message || "Analysis failed");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto py-20 text-center">
        <Loader2 className="w-12 h-12 animate-spin mx-auto mb-4 text-blue-600" />
        <h2 className="text-lg font-bold text-navy-900">Analyzing document…</h2>
        <p className="text-gray-600">This may take a moment.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto py-20 text-center">
        <div className="w-12 h-12 mx-auto mb-4 text-red-500">
          <svg className="w-full h-full" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3" />
          </svg>
        </div>
        <h2 className="text-lg font-bold text-navy-900">Error</h2>
        <p className="text-gray-600">{error}</p>
        <Button onClick={startAnalysis}>Retry</Button>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="max-w-2xl mx-auto py-20 text-center">
        <div className="w-12 h-12 mx-auto mb-4 text-gray-400">
          <svg className="w-full h-full" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h2 className="text-lg font-bold text-navy-900">No analysis yet</h2>
        <Button onClick={startAnalysis}>Start Analysis</Button>
      </div>
    );
  }

  const clauses = analysis.clauses || [];
  const high = clauses.filter((c: any) => c.risk_level === "HIGH" || c.risk_level === "CRITICAL").length;

  return (
    <div className="max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-navy-900">Analysis Results</h1>
          <p className="text-gray-600 text-sm">
            Document analyzed {formatDate(analysis.created_at)} • Mode:{" "}
            {analysis.llm_mode}
          </p>
        </div>
        <Button
          onClick={() => navigate(`/results/${analysis.id}`)}
        >
          View Full Report <ArrowRight className="ml-2 w-4 h-4" />
        </Button>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <StatCard title="Total Clauses" value={clauses.length} />
        <StatCard title="High / Critical" value={high} color="text-red-600" />
        <StatCard title="Mode" value={analysis.llm_mode} />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
        <h2 className="text-lg font-bold text-navy-900 mb-4">Executive Summary</h2>
        <p className="text-gray-700">{analysis.summary || "Summary not available."}</p>
      </div>
    </div>
  );
}

function StatCard({ title, value, color }: { title: string; value: number | string; color?: string }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-sm text-gray-500">{title}</p>
      <p className={`text-2xl font-bold text-navy-900 mt-1 ${color || ""}`}>{value}</p>
    </div>
  );
}
