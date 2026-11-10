import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { api } from "@/services/api";
import { formatDate } from "@/utils/format";
import { RiskDistributionChart, CategoryDistributionChart } from "@/components/charts/RiskDistributionChart";
import { FileText, Download, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/components/ui/toast";
import { Skeleton } from "@/components/ui/skeleton";

export function ResultsDashboard() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!analysisId) return;
    loadAnalysis();
  }, [analysisId]);

  const loadAnalysis = async () => {
    try {
      const data = await api.getAnalysis(Number(analysisId));
      setAnalysis(data);
    } catch (err: any) {
      setError(err.message || "Failed to load results");
      toast.error(err.message || "Failed to load results");
    } finally {
      setLoading(false);
    }
  };

  const handleExportPdf = () => {
    const base = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api";
    const url = `${base}/documents/${analysis?.document_id}/export?format=pdf`;
    toast.promise(
      fetch(url).then(async (res) => {
        if (!res.ok) throw new Error("PDF export failed");
        const blob = await res.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = `clauseclear-report-${analysisId}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        return true;
      }),
      {
        loading: "Generating PDF report…",
        success: "PDF report downloaded",
        error: "Failed to download PDF report",
      },
    );
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto py-10">
        <h1 className="text-2xl font-bold text-navy-900 mb-6">Analysis Report</h1>
        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <Skeleton variant="block" className="h-8 w-1/3 mb-3" />
            <div className="space-y-3">
              <div className="h-16 bg-gray-200 rounded-lg" />
              <div className="h-16 bg-gray-200 rounded-lg" />
            </div>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-6">
            <div className="h-48 bg-gray-200 rounded-lg" />
          </div>
        </div>
      </div>
  );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto py-10 text-center">
        <p className="text-red-600">{error}</p>
        <Button onClick={() => window.location.reload()}>Retry</Button>
      </div>
    );
  }

  if (!analysis) return null;

  const clauses = analysis.clauses || [];
const dist = analysis.risk_distribution || {};
const total = clauses.length || 1;
const concerning = clauses.filter(
  (c: any) => c.risk_level === "HIGH" || c.risk_level === "CRITICAL",
).length;

return (
  <div className="max-w-5xl mx-auto space-y-8">
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold text-navy-900">Analysis Report</h1>
        <p className="text-gray-600 text-sm">
          {formatDate(analysis.created_at)} •
          <Badge variant="secondary">{analysis.llm_mode} mode</Badge>
        </p>
      </div>
      <div className="flex gap-2">
        <Link to="/compare" className="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700">
          <FileText className="w-4 h-4 mr-2" /> Compare Versions
        </Link>
        <Button onClick={handleExportPdf}>
          <Download className="w-4 h-4 mr-2" /> Download PDF
        </Button>
      </div>
    </div>

    {/* Stats cards */}
    <div className="grid md:grid-cols-4 gap-4">
      <StatCard title="Total Clauses" value={total} />
      <StatCard title="High / Critical" value={concerning} color="text-red-600" />
      <StatCard title="Analysis Mode" value={analysis.llm_mode} />
      <StatCard title="Explanation" value={analysis.explanation_level} />
    </div>

    {/* Executive summary */}
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
      <h3 className="text-lg font-bold text-navy-900 mb-3">Executive Summary</h3>
      <p className="text-gray-700">{analysis.summary || "Summary not available."}</p>
      {analysis.llm_mode === "rule-based" && (
        <p className="text-xs text-gray-500 mt-3">
          Simplifications generated using rule-based fallback (no LLM configured).
        </p>
      )}
    </div>

    {/* Charts */}
    <RiskDistributionChart distribution={dist} />
    <CategoryDistributionChart categories={getCategoryDistribution(clauses)} />

    {/* Clause explorer */}
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-navy-900">Clause Explorer ({total})</h3>
        <span className="text-sm text-gray-500">
          {concerning} concerning clause(s)
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="pb-2 text-gray-500 font-medium">Category</th>
              <th className="pb-2 text-gray-500 font-medium">Risk</th>
              <th className="pb-2 text-gray-500 font-medium">Original</th>
              <th className="pb-2 text-gray-500 font-medium">Simplified</th>
              <th className="pb-2 text-gray-500 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {clauses.map((clause: any) => (
              <tr key={clause.id} className="border-b border-gray-100 hover:bg-gray-50 group">
                <td className="py-3">
                  <span className="text-sm font-medium text-navy-900">
                    {clause.category.replace(/_/g, " ")}
                  </span>
                </td>
                <td className="py-3">
                  <Badge variant="default" className={riskColor(clause.risk_level)}>
                    {clause.risk_level}
                  </Badge>
                </td>
                <td className="py-3 max-w-[200px]">
                  <span className="text-gray-700">
                    {clause.original_text.slice(0, 120)}{clause.original_text.length > 120 ? "…" : ""}
                  </span>
                </td>
                <td className="py-3 max-w-[220px]">
                  <span className="text-gray-600">
                    {(clause.simplified_text || "—").slice(0, 120)}
                    {(clause.simplified_text || "").length > 120 ? "…" : ""}
                  </span>
                </td>
                <td className="py-3 text-right">
                  <Link
                    to={`/clause/${clause.id}`}
                    className="text-blue-600 text-xs hover:underline"
                  >
                    View <ChevronRight className="w-3 h-3 ml-1" />
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>

    <div className="bg-gray-50 rounded-lg p-4 text-xs text-gray-500">
      Informational explanations only — not legal advice. Consult a qualified attorney for legal interpretation.
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

function riskColor(level: string | null | undefined): string {
  switch (level) {
    case "LOW": return "text-green-700 bg-green-100 border-green-200";
    case "MEDIUM": return "text-amber-700 bg-amber-100 border-amber-200";
    case "HIGH": return "text-orange-700 bg-orange-100 border-orange-200";
    case "CRITICAL": return "text-red-700 bg-red-100 border-red-200";
    default: return "text-gray-600 bg-gray-100 border-gray-200";
  }
}

function getCategoryDistribution(clauses: any[]): Record<string, number> {
  const cats: Record<string, number> = {};
  clauses.forEach((c) => {
    cats[c.category] = (cats[c.category] || 0) + 1;
  });
  return cats;
}
