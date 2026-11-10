import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "@/services/api";
import { toast } from "@/components/ui/toast";
import { Button } from "@/components/ui/button";
import { Dialog } from "@/components/ui/dialog";
import { SkeletonTableRow } from "@/components/ui/skeleton";
import { Trash2, Download, FileText, Eye } from "lucide-react";

export function DocumentsPage() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [filterStatus, setFilterStatus] = useState<string | undefined>();
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; id?: number }>({ open: false, id: undefined });

  const {
    data: documents,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["documents", page, filterStatus],
    queryFn: () =>
      api.listDocuments({ page, page_size: 20, status: filterStatus }),
  });

  const deleteDoc = useMutation({
    mutationFn: (id: number) => api.deleteDocument(id),
    onSuccess: () => {
      toast.success("Document deleted");
      queryClient.invalidateQueries({ queryKey: ["documents"] });
      setDeleteDialog({ open: false, id: undefined });
    },
    onError: (err: any) => toast.error(err.message || "Delete failed"),
  });

  const handleDelete = (id: number) => {
    setDeleteDialog({ open: true, id });
  };

  const confirmDelete = () => {
    const delId = deleteDialog.id;
    if (delId !== undefined) {
      deleteDoc.mutate(delId);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto py-10">
        <h1 className="text-2xl font-bold text-navy-900 mb-6">Documents</h1>
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => <SkeletonTableRow key={i} />)}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto py-10 text-center">
        <p className="text-red-600">{error.message}</p>
        <Button onClick={() => window.location.reload()}>Retry</Button>
      </div>
    );
  }

  const items = documents?.items || [];
  const totalPages = documents?.pages || 1;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-navy-900">Documents</h1>
          <p className="text-gray-600 text-sm">
            {documents?.total} document(s) — page {page} of {totalPages}
          </p>
        </div>
        <Link to="/" className="px-3.5 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700">
          New Analysis
        </Link>
      </div>

      <div className="flex gap-2 mb-4">
        <Button variant="outline" size="sm" onClick={() => setFilterStatus(undefined)}>
          All
        </Button>
        <Button variant="outline" size="sm" onClick={() => setFilterStatus("extracted")}>
          Extracted
        </Button>
        <Button variant="outline" size="sm" onClick={() => setFilterStatus("failed")}>
          Failed
        </Button>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="px-4 py-3 font-medium text-gray-600 w-1/3">Document</th>
              <th className="px-4 py-3 font-medium text-gray-600">Type</th>
              <th className="px-4 py-3 font-medium text-gray-600">Status</th>
              <th className="px-4 py-3 font-medium text-gray-600 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                  No documents yet. Start by analyzing a URL, file, or text.
                </td>
              </tr>
            ) : (
              items.map((doc) => (
                <tr key={doc.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-gray-400" />
                      <span className="text-navy-900 font-medium">{doc.filename}</span>
                    </div>
                    {doc.source_url && (
                      <p className="text-xs text-gray-500 truncate max-w-xs">{doc.source_url}</p>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-gray-500 capitalize">{doc.source_type}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={cn(
                        "px-2 py-1 rounded text-xs font-medium border",
                        doc.status === "extracted"
                          ? "bg-green-50 text-green-700 border-green-200"
                          : doc.status === "failed"
                            ? "bg-red-50 text-red-700 border-red-200"
                            : "bg-gray-50 text-gray-600 border-gray-200",
                      )}
                    >
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link to={`/results/${doc.id}`} className="text-blue-600 hover:underline text-sm">
                        <Eye className="w-4 h-4 mr-1" /> View
                      </Link>
                      <button
                        onClick={() => handleDelete(doc.id)}
                        className="text-red-600 hover:underline text-sm"
                      >
                        <Trash2 className="w-4 h-4 mr-1" /> Delete
                      </button>
                      <a
                        href={`${import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000/api"}/documents/${doc.id}/export?format=pdf`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline text-sm"
                      >
                        <Download className="w-4 h-4 mr-1" /> PDF
                      </a>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-4">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Prev
          </button>
          <span className="text-sm text-gray-600">Page {page} of {totalPages}</span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-3 py-1.5 text-sm border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}

      <Dialog open={deleteDialog.open} onOpenChange={(o) => setDeleteDialog({ open: o, id: deleteDialog.id })}>
        <h3 className="text-lg font-bold text-navy-900 mb-2">Delete document?</h3>
        <p className="text-gray-600 text-sm mb-6">
          This will permanently delete the document and its analysis. This cannot be undone.
        </p>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => setDeleteDialog({ open: false, id: undefined })}>
            Cancel
          </Button>
          <Button onClick={confirmDelete} disabled={deleteDoc.isPending}>
            {deleteDoc.isPending ? "Deleting…" : "Delete"}
          </Button>
        </div>
      </Dialog>
    </div>
  );
}

function cn(...classes: (string | boolean | undefined | null)[]) {
  return classes.filter(Boolean).join(" ");
}
