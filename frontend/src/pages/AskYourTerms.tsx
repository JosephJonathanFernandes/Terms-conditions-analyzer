import { useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "@/services/api";
import { MessageCircle, Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "@/components/ui/toast";

export function AskYourTermsPage() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const id = analysisId ? Number(analysisId) : 0;
  return <AskYourTerms analysisId={id} />;
}

export function AskYourTerms({ analysisId }: { analysisId: number }) {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [citations, setCitations] = useState<any[]>([]);
  const [doesNotSpecify, setDoesNotSpecify] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const suggested = [
    "Can this company sell or share my personal data?",
    "Can I delete my account?",
    "Can they automatically renew my subscription?",
    "Do I get a refund if I cancel?",
    "Who owns the content I upload?",
    "Can they terminate my account without warning?",
    "Can they change these terms whenever they want?",
  ];

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    setError("");
    setLoading(true);
    setAnswer(null);
    try {
      const res = await api.chat(analysisId, question);
      setAnswer(res.answer);
      setCitations(res.citations);
      setDoesNotSpecify(res.document_does_not_specify);
      toast.success("Answer received");
    } catch (err: any) {
      setError(err.message || "Failed to get answer");
      toast.error(err.message || "Failed to get answer");
    } finally {
      setLoading(false);
    }
  };

  const copyAnswer = () => {
    if (!answer) return;
    navigator.clipboard.writeText(answer);
    toast.success("Copied to clipboard");
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <MessageCircle className="w-5 h-5 text-blue-600" />
          <h2 className="text-xl font-bold text-navy-900">Ask Your Terms</h2>
        </div>
        <p className="text-gray-600 text-sm mb-4">
          Ask questions about the document. Answers are grounded in the extracted clauses with citations.
        </p>

        <form onSubmit={handleAsk} className="space-y-3">
          <div className="relative">
            <MessageCircle className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
            <input
              className="input pl-10"
              placeholder="e.g. Can they automatically renew my subscription?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={loading}
            />
            <Button
              type="submit"
              className="absolute right-2 top-2 text-xs px-3"
              disabled={loading || !question.trim()}
            >
              {loading ? "…" : "Ask"}
            </Button>
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-800 text-sm">
              {error}
            </div>
          )}
        </form>

        <div className="mt-6">
          <p className="text-sm font-medium text-gray-600 mb-2">Suggested questions</p>
          <div className="flex flex-wrap gap-2">
            {suggested.map((q) => (
              <button
                key={q}
                onClick={() => setQuestion(q)}
                disabled={loading}
                className="px-3 py-2 text-xs text-left w-auto bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 bg-blue-600 rounded-full animate-pulse" />
            <span className="text-sm text-gray-600">Generating answer…</span>
          </div>
        </div>
      )}

      {answer && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-navy-900">Answer</h3>
            <div className="flex gap-2">
              {doesNotSpecify && (
                <Badge variant="destructive" className="text-xs">
                  Document does not specify
                </Badge>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={copyAnswer}
              >
                <Copy className="w-3 h-3 mr-1" /> Copy
              </Button>
            </div>
          </div>
          <div className="prose prose-sm text-gray-700 mb-4 whitespace-pre-wrap">
            {answer}
          </div>

          {citations.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Sources</p>
              <div className="space-y-2">
                {citations.map((c) => (
                  <div key={c.clause_id} className="p-3 rounded-lg bg-gray-50 border border-gray-100">
                    <div className="flex justify-between mb-1">
                      <span className="text-xs font-medium text-blue-600">{c.category}</span>
                      {c.source_location && (
                        <span className="text-xs text-gray-500">{c.source_location}</span>
                      )}
                    </div>
                    <div className="text-sm text-gray-700 italic">
                      “{c.quote}”
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
