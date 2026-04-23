import { renderHook, act } from "@testing-library/react";
import { useAnalysis } from "../../hooks/useAnalysis";
import apiClient from "../../api/client";
import type { AnalysisResult } from "../../types";

vi.mock("../../api/client", () => ({
  default: { post: vi.fn(), get: vi.fn() },
}));

const mockPost = vi.mocked(apiClient.post);

const fakeResult: AnalysisResult = {
  id: "result-123",
  overall_score: 82,
  categories: [{ name: "Skills Match", score: 85, rationale: "Good" }],
  skills: ["Python", "AWS"],
  experience: [{ title: "Engineer", company: "Acme", duration: "2020-2024" }],
  education: [{ degree: "BS CS", institution: "State U", year: "2018" }],
  suggestions: ["Add quantifiable achievements"],
  created_at: "2026-04-17T10:00:00Z",
  file_name: "resume.pdf",
  job_description: "We need a Python developer",
};

beforeEach(() => vi.useFakeTimers());
afterEach(() => {
  vi.useRealTimers();
  vi.restoreAllMocks();
});

describe("useAnalysis", () => {
  it("has correct initial state", () => {
    const { result } = renderHook(() => useAnalysis());
    expect(result.current.loading).toBe(false);
    expect(result.current.status).toBe("");
    expect(result.current.result).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it("analyzes successfully and returns result", async () => {
    mockPost.mockResolvedValueOnce({ data: fakeResult });

    const { result } = renderHook(() => useAnalysis());

    let returned: AnalysisResult | null = null;
    await act(async () => {
      vi.runAllTimers();
      returned = await result.current.analyze("uploads/abc/resume.pdf", "We need a Python developer with AWS");
    });

    expect(returned).toEqual(fakeResult);
    expect(result.current.result).toEqual(fakeResult);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(mockPost).toHaveBeenCalledWith("/analyze", {
      s3_key: "uploads/abc/resume.pdf",
      job_description: "We need a Python developer with AWS",
    });
  });

  it("sets error when analysis fails", async () => {
    mockPost.mockRejectedValueOnce(new Error("Analysis failed"));

    const { result } = renderHook(() => useAnalysis());

    await act(async () => {
      vi.runAllTimers();
      await result.current.analyze("uploads/abc/resume.pdf", "job desc");
    });

    expect(result.current.error).toBe("Analysis failed");
    expect(result.current.result).toBeNull();
    expect(result.current.loading).toBe(false);
  });

  it("reset() restores initial state", async () => {
    mockPost.mockRejectedValueOnce(new Error("fail"));

    const { result } = renderHook(() => useAnalysis());

    await act(async () => {
      vi.runAllTimers();
      await result.current.analyze("key", "desc");
    });

    act(() => result.current.reset());
    expect(result.current.error).toBeNull();
    expect(result.current.result).toBeNull();
    expect(result.current.loading).toBe(false);
  });
});
