import { useState } from "react";
import apiClient from "../api/client";
import type { AnalysisResult } from "../types";

interface AnalysisState {
  loading: boolean;
  status: string;
  result: AnalysisResult | null;
  error: string | null;
}

export function useAnalysis() {
  const [state, setState] = useState<AnalysisState>({
    loading: false,
    status: "",
    result: null,
    error: null,
  });

  const analyze = async (s3Key: string, jobDescription: string): Promise<AnalysisResult | null> => {
    setState({ loading: true, status: "Extracting text from resume...", result: null, error: null });

    try {
      setTimeout(() => setState((p) => ({ ...p, status: "Analyzing with AI..." })), 2000);

      const { data } = await apiClient.post<AnalysisResult>("/analyze", {
        s3_key: s3Key,
        job_description: jobDescription,
      });

      setState({ loading: false, status: "", result: data, error: null });
      return data;
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Analysis failed. Please try again.";
      setState({ loading: false, status: "", result: null, error: message });
      return null;
    }
  };

  const reset = () => setState({ loading: false, status: "", result: null, error: null });

  return { ...state, analyze, reset };
}
