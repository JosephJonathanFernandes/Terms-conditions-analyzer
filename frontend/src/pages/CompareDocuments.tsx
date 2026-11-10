import { useState } from "react";
import { api } from "@/services/api";
import { categoryLabel } from "@/utils/format";
import { ArrowRightLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/toast";

export function CompareDocuments() {
  const [analysisIdA, setAnalysisIdA] = useState("");
  const [analysisIdB, setAnalysisIdB] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const res = await api.compare(Number(analysisIdA), Number(analysisIdB));
      setResult(res);
      if (res.added.length === 0 && res.removed.length === 0 && res.modified.length === 0) {
        toast.info("No differences detected between the two documents");
      } else {
        toast.success("Comparison complete");
      }
    } catch (err: any) {
      setError(err.message || "Comparison failed");
      toast.error(err.message || "Comparison failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <ArrowRightLeft className="w-5 h-5 text-blue-600" />
          <h2 className="text-xl font-bold text-navy-900">Compare Documents</h2>
        </div>
        <p className="text-gray-600 text-sm mb-6">
          Compare two versions of the same Terms &amp; Conditions to see what changed.
        </p>

        <form onSubmit={handleCompare} className="grid md:grid-cols-3 gap-4 items-end">
          <div className="flex flex-col">
            <label className="text-sm font-medium text-gray-700 mb-1">Version A (Analysis ID)</label>
            <input
              className="input"
              type="number"
              placeholder="e.g. 1"
              value={analysisIdA}
              onChange={(e) => setAnalysisIdA(e.target.value)}
            />
          </div>
          <div className="flex flex-col">
            <label className="text-sm font-medium text-gray-700 mb-1">Version B (Analysis ID)</label>
            <input
              className="input"
              type="number"
              placeholder="e.g. 2"
              value={analysisIdB}
              onChange={(e) => setAnalysisIdB(e.target.value)}
            />
          </div>
          <Button
            type="submit"
            className="w-full"
            disabled={loading || !analysisIdA || !analysisIdB}
          >
            {loading ? "Comparing…" : "Compare"}
          </Button>
        </form>

        {error && (
          <div className="mt-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm">
            {error}
          </div>
        )}
      </div>

      {loading && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3 text-gray-600 text-sm">
            <div className="w-3 h-3 bg-blue-600 rounded-full animate-pulse" />
            Comparing documents…
          </div>
        </div>
      )}

      {result && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h3 className="text-lg font-bold text-navy-900 mb-4">Comparison Results</h3>
          {result.impact_summary && (
            <div className="mb-6 p-4 rounded-lg bg-blue-50 border border-blue-100 text-blue-800 text-sm">
              {result.impact_summary}
            </div>
          )}
          <div className="grid md:grid-cols-3 gap-4">
            <ChangeList title="Added" items={result.added} color="bg-green-50 text-green-800 border-green-200" />
            <ChangeList title="Removed" items={result.removed} color="bg-red-50 text-red-800 border-red-200" />
            <ChangeList title="Modified" items={result.modified} color="bg-amber-50 text-amber-800 border-amber-200" />
          </div>
        </div>
      )}
    </div>
  );
}

function ChangeList({ title, items, color }: { title: string; items: any[]; color: string }) {
  return (
    <div className={cn(`border rounded-xl p-4 ${color}`)}>
      <h4 className="text-sm font-bold mb-3 uppercase tracking-wider">{title}</h4>
      {items.length === 0 ? (
        <p className="text-xs text-gray-500">None</p>
      ) : (
        <ul className="space-y-2 text-sm">
          {items.map((item) => (
            <li key={item.clause_id} className="border-b pb-1 last:border-0">
              <span className="font-medium">{categoryLabel(item.category)}</span>{" "}
              <span className="text-xs text-gray-500">({item.change_type})</span>
              {item.impact && <p className="text-xs text-gray-600 mt-1">{item.impact}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}
