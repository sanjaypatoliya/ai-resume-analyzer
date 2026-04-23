import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { UploadZone } from "../components/UploadZone";
import { useUpload } from "../hooks/useUpload";
import { useAnalysis } from "../hooks/useAnalysis";

export function HomePage() {
  const navigate = useNavigate();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const { uploading, progress, s3Key, error: uploadError, upload, reset: resetUpload } = useUpload();
  const { loading: analyzing, status, error: analysisError, analyze } = useAnalysis();

  const handleFileSelected = async (file: File) => {
    setSelectedFile(file);
    resetUpload();
    await upload(file);
  };

  const handleSubmit = async () => {
    if (!s3Key || !jobDescription.trim()) return;

    const result = await analyze(s3Key, jobDescription);
    if (result) {
      navigate(`/results?id=${result.id}`);
    }
  };

  const isReady = s3Key && jobDescription.trim().length > 50 && !uploading && !analyzing;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-3xl mx-auto px-4 py-16">

        {/* Nav */}
        <div className="flex justify-end mb-4">
          <button
            onClick={() => navigate("/history")}
            className="px-4 py-2 text-sm text-blue-600 border border-blue-200 rounded-lg hover:bg-blue-50"
          >
            View History
          </button>
        </div>

        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">Resume Analyzer</h1>
          <p className="text-lg text-gray-500">
            Upload your resume and a job description — AI scores your match and suggests improvements.
          </p>
          <div className="flex justify-center gap-2 mt-4 flex-wrap">
            {["AWS Textract", "AWS Bedrock", "Claude AI"].map((tag) => (
              <span key={tag} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                {tag}
              </span>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 space-y-8">

          {/* Step 1 — Upload */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              1. Upload Resume (PDF)
            </label>
            <UploadZone
              onFileSelected={handleFileSelected}
              uploading={uploading}
              progress={progress}
              fileName={selectedFile?.name ?? null}
            />
            {s3Key && !uploading && (
              <p className="mt-2 text-sm text-green-600 font-medium">Resume uploaded successfully</p>
            )}
            {uploadError && (
              <p className="mt-2 text-sm text-red-500">{uploadError}</p>
            )}
          </div>

          {/* Step 2 — Job Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              2. Paste Job Description
            </label>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              rows={8}
              placeholder="Paste the full job description here..."
              className="w-full border border-gray-200 rounded-xl p-4 text-sm text-gray-700
                         placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500
                         focus:border-transparent resize-none"
            />
            <p className="mt-1 text-xs text-gray-400">
              {jobDescription.length} characters {jobDescription.length < 50 ? "— add more for better results" : ""}
            </p>
          </div>

          {/* Error */}
          {analysisError && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-sm text-red-600">{analysisError}</p>
            </div>
          )}

          {/* Analyzing status */}
          {analyzing && (
            <div className="flex items-center gap-3 text-sm text-blue-600">
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span>{status || "Analyzing..."}</span>
            </div>
          )}

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={!isReady}
            className={`w-full py-4 rounded-xl font-semibold text-white transition-all
              ${isReady
                ? "bg-blue-600 hover:bg-blue-700 shadow-md hover:shadow-lg"
                : "bg-gray-200 text-gray-400 cursor-not-allowed"}`}
          >
            {analyzing ? "Analyzing..." : "Analyze Resume"}
          </button>
        </div>
      </div>
    </div>
  );
}
