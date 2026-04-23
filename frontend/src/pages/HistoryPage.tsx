import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useHistory } from "../hooks/useHistory";
import { useDeleteHistory } from "../hooks/useDeleteHistory";

const scoreColor = (score: number) =>
  score >= 70 ? "text-green-600" : score >= 40 ? "text-yellow-600" : "text-red-600";

const scoreBg = (score: number) =>
  score >= 70 ? "bg-green-50 border-green-200" : score >= 40 ? "bg-yellow-50 border-yellow-200" : "bg-red-50 border-red-200";

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function HistoryPage() {
  const navigate = useNavigate();
  const { data, isLoading, isError } = useHistory();
  const { mutate: deleteItems, isPending: isDeleting } = useDeleteHistory();
  const [confirmId, setConfirmId] = useState<string | null>(null);

  const handleSingleDelete = (id: string) => {
    deleteItems([id], {
      onSuccess: () => setConfirmId(null),
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-4xl mx-auto px-4 py-12">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analysis History</h1>
            <p className="text-sm text-gray-400 mt-1">Your recent resume analyses</p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate("/")}
              className="px-4 py-2 text-sm text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50"
            >
              Analyze Resume
            </button>
          </div>
        </div>

        {/* Loading */}
        {isLoading && (
          <div className="flex items-center justify-center py-24">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          </div>
        )}

        {/* Error */}
        {isError && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <p className="text-red-600 text-sm">Failed to load history. Make sure the backend is running.</p>
          </div>
        )}

        {/* Empty */}
        {!isLoading && !isError && data?.items.length === 0 && (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-12 text-center">
            <p className="text-gray-400 text-lg mb-4">No analyses yet</p>
            <button
              onClick={() => navigate("/")}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
            >
              Analyze your first resume
            </button>
          </div>
        )}

        {/* History List */}
        {!isLoading && !isError && data && data.items.length > 0 && (
          <div className="space-y-4">
            <p className="text-sm text-gray-400">{data.total} result{data.total !== 1 ? "s" : ""}</p>

            {data.items.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 flex flex-col gap-3 transition-shadow hover:shadow-md sm:flex-row sm:items-center sm:justify-between"
              >
                {/* Score + file info */}
                <div className="flex items-center gap-3 min-w-0">
                  <div className={`w-12 h-12 rounded-xl border flex items-center justify-center flex-shrink-0 ${scoreBg(item.overall_score)}`}>
                    <span className={`text-lg font-bold ${scoreColor(item.overall_score)}`}>
                      {item.overall_score}
                    </span>
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">{item.file_name}</p>
                    <p className="text-xs text-gray-400 mt-0.5 whitespace-nowrap">{formatDate(item.created_at)}</p>
                  </div>
                </div>

                {/* Score label + action buttons */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className={`text-xs font-semibold px-3 py-1 rounded-full border ${scoreBg(item.overall_score)} ${scoreColor(item.overall_score)}`}>
                    {item.overall_score >= 70 ? "Good Match" : item.overall_score >= 40 ? "Partial Match" : "Low Match"}
                  </span>

                  <button
                    onClick={() => navigate(`/results?id=${item.id}`)}
                    className="px-3 py-1.5 text-xs text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50"
                  >
                    View
                  </button>

                  {confirmId === item.id ? (
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => handleSingleDelete(item.id)}
                        disabled={isDeleting}
                        className="px-3 py-1.5 text-xs text-white bg-red-500 rounded-lg hover:bg-red-600 disabled:opacity-50"
                      >
                        {isDeleting ? "..." : "Confirm"}
                      </button>
                      <button
                        onClick={() => setConfirmId(null)}
                        className="px-3 py-1.5 text-xs text-gray-500 border border-gray-200 rounded-lg hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setConfirmId(item.id)}
                      className="px-3 py-1.5 text-xs text-red-500 border border-red-200 rounded-lg hover:bg-red-50"
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
