import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api } from "@/services/api";
import { formatDate } from "@/utils/format";
import { RefreshCw, Trash2, Eye } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "@/components/ui/toast";
import { Dialog } from "@/components/ui/dialog";
import { SkeletonTableRow } from "@/components/ui/skeleton";

export function HistoryPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; id?: number }>({ open: false, id: undefined });

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await api.history();
      setItems(data);
    } catch (err: any) {
      setError(err.message || "Failed to load history");
      toast.error(err.message || "Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (id: number) => {
    setDeleteDialog({ open: true, id });
  };

  const confirmDelete = async () => {
    if (!deleteDialog.id) return;
    try {
      await api.deleteAnalysis(deleteDialog.id);
      toast.success("Analysis deleted");
      setItems(items.filter((i) => i.id !== deleteDialog.id));
    } catch (err: any) {
      toast.error(err.message || "Delete failed");
    } finally {
      setDeleteDialog({ open: false, id: undefined });
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto py-10">
        <h1 className="text-2xl font-bold text-navy-900 mb-6">History</h1>
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => <SkeletonTableRow key={i} />)}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-5xl mx-auto py-10 text-center">
        <p className="text-red-600">{error}</p>
        <Button onClick={loadHistory}>Retry</Button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-navy-900">History</h1>
          <p className="text-gray-600 text-sm">{items.length} previous analysis(es)</p>
        </div>
        <Button onClick={loadHistory} size="sm">
          <RefreshCw className="w-4 h-4 mr-2" /> Refresh
        </Button>
      </div>

      {items.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <svg className="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="text-lg font-bold text-navy-900 mb-2">No previous analyses</h3>
          <p className="text-gray-500 text-sm">Analyze a document to see it here.</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-4 py-3 font-medium text-gray-600">Document</th>
                <th className="px-4 py-3 font-medium text-gray-600">Type</th>
                <th className="px-4 py-3 font-medium text-gray-600">Date</th>
                <th className="px-4 py-3 font-medium text-gray-600">Status</th>
                <th className="px-4 py-3 font-medium text-gray-600 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className="text-navy-900 font-medium">{item.filename}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-xs text-gray-500 capitalize">{item.source_type}</span>
                  </td>
                  <td className="px-4 py-3">{formatDate(item.created_at)}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 rounded text-xs font-medium border bg-gray-100 text-gray-600 border-gray-200">
                      {item.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Link to={`/results/${item.id}`} className="text-blue-600 hover:underline text-sm">
                        <Eye className="w-4 h-4 mr-1" /> View
                      </Link>
                      <button
                        onClick={() => handleDelete(item.id)}
                        className="text-red-600 hover:underline text-sm"
                      >
                        <Trash2 className="w-4 h-4 mr-1" /> Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Dialog open={deleteDialog.open} onOpenChange={(o) => setDeleteDialog({ open: o, id: deleteDialog.id })}>
        <h3 className="text-lg font-bold text-navy-900 mb-2">Delete analysis?</h3>
        <p className="text-gray-600 text-sm mb-6">
          This will permanently delete the analysis record. This cannot be undone.
        </p>
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => setDeleteDialog({ open: false, id: undefined })}>
            Cancel
          </Button>
          <Button onClick={confirmDelete} disabled={false}>
            Delete
          </Button>
        </div>
      </Dialog>
    </div>
  );
}
