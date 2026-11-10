import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Globe,
  Edit3,
  Zap,
  ShieldAlert,
} from "lucide-react";
import { api } from "@/services/api";
import { toast } from "@/components/ui/toast";
import { Dropzone } from "@/components/ui/dropzone";
import { Button } from "@/components/ui/button";

export function LandingPage() {
  const navigate = useNavigate();
  const [method, setMethod] = useState<"url" | "file" | "text">("url");
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [files, setFiles] = useState<File[]>([]);
  const [submitting, setSubmitting] = useState(false);

  const MAX_SIZE_MB = 25;

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    setSubmitting(true);
    try {
      const res = await api.ingestUrl(url);
      if (res.document_id) {
        toast.success("URL extracted successfully");
        navigate(`/results/${res.document_id}`);
      } else {
        toast.error(res.message || "Extraction failed");
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to extract URL");
    } finally {
      setSubmitting(false);
    }
  };

  const handleFileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (files.length === 0) return;
    setSubmitting(true);
    try {
      // Upload the first file (multi-file support can be added later)
      const res = await api.ingestFile(files[0]);
      if (res.document_id) {
        toast.success(`"${files[0].name}" extracted successfully`);
        navigate(`/results/${res.document_id}`);
      } else {
        toast.error(res.message || "Extraction failed");
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to upload file");
    } finally {
      setSubmitting(false);
    }
  };

  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    setSubmitting(true);
    try {
      const res = await api.ingestText(text);
      if (res.document_id) {
        toast.success("Text ingested successfully");
        navigate(`/results/${res.document_id}`);
      } else {
        toast.error(res.message || "Ingestion failed");
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to ingest text");
    } finally {
      setSubmitting(false);
    }
  };

  const methodLabels: Record<string, { icon: React.ReactNode; label: string }> = {
    url: { icon: <Globe className="w-5 h-5" />, label: "Website URL" },
    file: { icon: <FileText className="w-5 h-5" />, label: "Upload Document" },
    text: { icon: <Edit3 className="w-5 h-5" />, label: "Paste Text" },
  };

  const MethodButton = ({ key, active }: { key: "url" | "file" | "text"; active: boolean }) => {
    const m = methodLabels[key];
    return (
      <button
        onClick={() => setMethod(key)}
        className={cn(
          "w-full px-4 py-3 rounded-lg border text-sm font-medium transition-colors text-left",
          active
            ? "bg-blue-600 text-white border-blue-600"
            : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50",
        )}
      >
        <span className="flex items-center gap-2">{m.icon} {m.label}</span>
      </button>
    );
  };

  return (
    <div className="space-y-8">
      {/* Hero */}
      <section className="mt-6">
        <div className="max-w-3xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-xs font-semibold mb-4">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            Rule-based by default — no LLM required
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-navy-900 tracking-tight mb-6">
            ClauseClear
          </h1>
          <p className="text-lg text-gray-600 mb-6 max-w-2xl mx-auto">
            Understand what you&apos;re agreeing to before you accept Terms &
            Conditions, Privacy Policies, and subscription agreements.
          </p>
          <p className="text-sm text-gray-500 mb-8">
            Informational explanations only — not legal advice.
          </p>

          <div className="grid md:grid-cols-3 gap-3 mb-8">
            <MethodButton key="url" active={method === "url"} />
            <MethodButton key="file" active={method === "file"} />
            <MethodButton key="text" active={method === "text"} />
          </div>

          {method === "url" && (
            <form onSubmit={handleUrlSubmit} className="mt-4 max-w-md mx-auto space-y-3">
              <div className="relative">
                <Globe className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                <input
                  className="input pl-10"
                  placeholder="https://example.com/terms"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
              </div>
              <Button type="submit" className="w-full" disabled={!url || submitting}>
                {submitting ? "Extracting…" : "Analyze Website"}
              </Button>
            </form>
          )}

          {method === "file" && (
            <form onSubmit={handleFileSubmit} className="mt-4 max-w-md mx-auto space-y-4">
              <label className="text-sm font-medium text-gray-700">
                Upload PDF, DOCX, or TXT (max {MAX_SIZE_MB} MB each)
              </label>
              <Dropzone onFiles={setFiles} disabled={submitting} />
              <Button type="submit" className="w-full" disabled={files.length === 0 || submitting}>
                {submitting ? "Uploading…" : "Analyze Document"}
              </Button>
            </form>
          )}

          {method === "text" && (
            <form onSubmit={handleTextSubmit} className="mt-4 max-w-md mx-auto space-y-3">
              <textarea
                className="input h-56 resize-y"
                placeholder="Paste Terms & Conditions text here…"
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
              <Button type="submit" className="w-full" disabled={!text.trim() || submitting}>
                {submitting ? "Analyzing…" : "Analyze Text"}
              </Button>
            </form>
          )}
        </div>
      </section>

      {/* How it works */}
      <section className="py-12 border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-2xl font-bold text-navy-900 mb-8">How it works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureStep
              icon={<Globe className="w-6 h-6 text-blue-600" />}
              title="1. Extract"
              description="Enter a website URL, upload a PDF/DOCX/TXT, or paste text. We extract and clean the actual legal content."
            />
            <FeatureStep
              icon={<Zap className="w-6 h-6 text-purple-600" />}
              title="2. Analyze"
              description="Clauses are detected into 21 categories and assessed for risk using deterministic, explainable rules."
            />
            <FeatureStep
              icon={<ShieldAlert className="w-6 h-6 text-orange-600" />}
              title="3. Understand"
              description="See plain-language explanations, risk levels, and evidence — ask questions or download a report."
            />
          </div>
        </div>
      </section>
    </div>
  );
}

function FeatureStep({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <div className="bg-white p-6 rounded-xl border border-gray-200">
      <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-bold text-navy-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
}

function FileText(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  );
}

function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}
