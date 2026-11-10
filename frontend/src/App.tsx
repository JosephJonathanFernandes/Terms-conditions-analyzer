import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ErrorBoundary } from "react-error-boundary";
import type { FallbackProps } from "react-error-boundary";
import { Toaster } from "sonner";
import { Layout } from "@/components/layout/Navbar";
import { LandingPage } from "@/pages/LandingPage";
import { AnalysisPage } from "@/pages/AnalysisPage";
import { ResultsDashboard } from "@/pages/ResultsDashboard";
import { AskYourTermsPage } from "@/pages/AskYourTerms";
import { CompareDocuments } from "@/pages/CompareDocuments";
import { HistoryPage } from "@/pages/HistoryPage";
import { ClauseDetail } from "@/pages/ClauseDetail";
import { DocumentsPage } from "@/pages/DocumentsPage";
import { toast } from "@/components/ui/toast";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  const msg = error instanceof Error ? error.message : String(error);
  console.error("Error boundary caught:", msg);
  toast.error(msg);
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h2 className="text-xl font-bold text-navy-900 mb-2">Something went wrong</h2>
        <p className="text-gray-600 mb-4">{msg}</p>
        <button onClick={resetErrorBoundary} className="btn-primary">
          Try again
        </button>
      </div>
    </div>
  );
}

function AppWithProviders() {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster position="bottom-right" richColors closeButton />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/analysis/:documentId" element={<AnalysisPage />} />
            <Route path="/results/:analysisId" element={<ResultsDashboard />} />
            <Route path="/qa/:analysisId" element={<AskYourTermsPage />} />
            <Route path="/compare" element={<CompareDocuments />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/clause/:clauseId" element={<ClauseDetail />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default function App() {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <AppWithProviders />
    </ErrorBoundary>
  );
}
