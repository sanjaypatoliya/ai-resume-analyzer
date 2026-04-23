import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import apiClient from "../api/client";
import type { AnalysisResult } from "../types";

const scoreColor = (score: number) =>
  score >= 70 ? "text-green-600" : score >= 40 ? "text-yellow-600" : "text-red-600";

const barColor = (score: number) =>
  score >= 70 ? "bg-green-500" : score >= 40 ? "bg-yellow-500" : "bg-red-500";

export function ResultsPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const id = searchParams.get("id");

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showJobDesc, setShowJobDesc] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    apiClient
      .get<AnalysisResult>(`/history/${id}`)
      .then(({ data }) => setResult(data))
      .catch(() => setError("Failed to load result."))
      .finally(() => setLoading(false));
  }, [id]);

  if (!id) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500 mb-4">No result ID provided.</p>
          <button onClick={() => navigate("/")} className="text-blue-600 underline">
            Go back
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error ?? "Result not found."}</p>
          <button onClick={() => navigate("/")} className="text-blue-600 underline">
            Go back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-4xl mx-auto px-4 py-12">

        {/* Header */}
        <div className="flex flex-col gap-4 mb-8 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
            <p className="text-sm text-gray-400 mt-1">{result.file_name}</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => navigate("/history")}
              className="px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              View History
            </button>
            <button
              onClick={() => navigate("/")}
              className="px-4 py-2 text-sm text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50"
            >
              Analyze Another
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          {/* Overall Score */}
          <div className="md:col-span-1 bg-white rounded-2xl border border-gray-100 shadow-sm p-6 flex flex-col items-center justify-center">
            <p className="text-sm font-medium text-gray-500 mb-2">Overall Match</p>
            <p className={`text-7xl font-bold ${scoreColor(result.overall_score)}`}>{result.overall_score}</p>
            <p className="text-gray-400 text-sm mt-1">out of 100</p>
          </div>

          {/* Category Breakdown */}
          <div className="md:col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-4">Category Breakdown</h2>
            <div className="space-y-4">
              {result.categories.map((cat) => (
                <div key={cat.name}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600 font-medium">{cat.name}</span>
                    <span className={`font-semibold ${barColor(cat.score).replace("bg-", "text-")}`}>
                      {cat.score}
                    </span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all ${barColor(cat.score)}`}
                      style={{ width: `${cat.score}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-400 mt-1">{cat.rationale}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Skills */}
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-3">Extracted Skills</h2>
            <div className="flex flex-wrap gap-2">
              {result.skills.map((skill) => (
                <span key={skill} className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium">
                  {skill}
                </span>
              ))}
            </div>
          </div>

          {/* Suggestions */}
          <div className="md:col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <h2 className="font-semibold text-gray-800 mb-3">Improvement Suggestions</h2>
            <ol className="space-y-3">
              {result.suggestions.map((s, i) => (
                <li key={i} className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-700 rounded-full text-xs font-bold flex items-center justify-center">
                    {i + 1}
                  </span>
                  <p className="text-sm text-gray-600">{s}</p>
                </li>
              ))}
            </ol>
          </div>

          {/* Experience + Education — same row */}
          {result.experience.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h2 className="font-semibold text-gray-800 mb-3">Experience</h2>
              <div className="space-y-3">
                {result.experience.map((exp, i) => (
                  <div key={i} className="border-l-2 border-blue-200 pl-3">
                    <p className="text-sm font-medium text-gray-800">{exp.title}</p>
                    <p className="text-xs text-gray-500">{exp.company} · {exp.duration}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {result.education.length > 0 && (
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
              <h2 className="font-semibold text-gray-800 mb-3">Education</h2>
              <div className="space-y-3">
                {result.education.map((edu, i) => (
                  <div key={i} className="border-l-2 border-purple-200 pl-3">
                    <p className="text-sm font-medium text-gray-800">{edu.degree}</p>
                    <p className="text-xs text-gray-500">{edu.institution} · {edu.year}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Job Description */}
          <div className="md:col-span-3 bg-white rounded-2xl border border-gray-100 shadow-sm p-6">
            <button
              onClick={() => setShowJobDesc((prev) => !prev)}
              className="w-full flex items-center justify-between text-left"
            >
              <h2 className="font-semibold text-gray-800">Job Description</h2>
              <span className="text-xs text-blue-600">{showJobDesc ? "Hide" : "Show"}</span>
            </button>
            {showJobDesc && (
              <p className="mt-3 text-sm text-gray-600 whitespace-pre-wrap">{result.job_description}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
