import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { ResultsPage } from "../../pages/ResultsPage";
import apiClient from "../../api/client";
import type { AnalysisResult } from "../../types";

vi.mock("../../api/client", () => ({
  default: { post: vi.fn(), get: vi.fn() },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockGet = vi.mocked(apiClient.get);

const fakeResult: AnalysisResult = {
  id: "result-123",
  overall_score: 82,
  categories: [
    { name: "Skills Match", score: 85, rationale: "Strong Python skills" },
    { name: "Experience Level", score: 70, rationale: "5 years matches" },
  ],
  skills: ["Python", "AWS", "FastAPI"],
  experience: [{ title: "Senior Engineer", company: "Acme", duration: "2020-2024" }],
  education: [{ degree: "BS Computer Science", institution: "State University", year: "2018" }],
  suggestions: ["Add quantifiable achievements", "Include AWS certifications"],
  created_at: "2026-04-17T10:00:00Z",
  file_name: "my-resume.pdf",
  job_description: "We are looking for a Senior Python Developer with AWS experience.",
};

afterEach(() => vi.clearAllMocks());

function renderWithRoute(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path="/results" element={<ResultsPage />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("ResultsPage", () => {
  it("shows 'No result ID' message when no id param", () => {
    renderWithRoute("/results");
    expect(screen.getByText(/No result ID provided/i)).toBeInTheDocument();
  });

  it("shows Go back link when no id param", () => {
    renderWithRoute("/results");
    expect(screen.getByRole("button", { name: /Go back/i })).toBeInTheDocument();
  });

  it("shows loading spinner while fetching", () => {
    mockGet.mockReturnValueOnce(new Promise(() => {}));
    renderWithRoute("/results?id=result-123");
    expect(document.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("shows error when fetch fails", async () => {
    mockGet.mockRejectedValueOnce(new Error("Not found"));
    renderWithRoute("/results?id=result-123");

    await waitFor(() =>
      expect(screen.getByText("Failed to load result.")).toBeInTheDocument()
    );
  });

  it("renders overall score after successful fetch", async () => {
    mockGet.mockResolvedValueOnce({ data: fakeResult });
    renderWithRoute("/results?id=result-123");

    await waitFor(() =>
      expect(screen.getByText("82")).toBeInTheDocument()
    );
    expect(screen.getByText("my-resume.pdf")).toBeInTheDocument();
  });

  it("renders categories breakdown", async () => {
    mockGet.mockResolvedValueOnce({ data: fakeResult });
    renderWithRoute("/results?id=result-123");

    await waitFor(() => screen.getByText("Skills Match"));
    expect(screen.getByText("Strong Python skills")).toBeInTheDocument();
  });

  it("renders skills tags", async () => {
    mockGet.mockResolvedValueOnce({ data: fakeResult });
    renderWithRoute("/results?id=result-123");

    await waitFor(() => screen.getByText("Python"));
    expect(screen.getByText("AWS")).toBeInTheDocument();
    expect(screen.getByText("FastAPI")).toBeInTheDocument();
  });

  it("renders suggestions list", async () => {
    mockGet.mockResolvedValueOnce({ data: fakeResult });
    renderWithRoute("/results?id=result-123");

    await waitFor(() => screen.getByText("Add quantifiable achievements"));
    expect(screen.getByText("Include AWS certifications")).toBeInTheDocument();
  });

  it("toggles job description visibility", async () => {
    mockGet.mockResolvedValueOnce({ data: fakeResult });
    renderWithRoute("/results?id=result-123");

    await waitFor(() => screen.getByText("Job Description"));

    expect(screen.queryByText(fakeResult.job_description)).not.toBeInTheDocument();

    fireEvent.click(screen.getByText("Show"));
    expect(screen.getByText(fakeResult.job_description)).toBeInTheDocument();

    fireEvent.click(screen.getByText("Hide"));
    expect(screen.queryByText(fakeResult.job_description)).not.toBeInTheDocument();
  });

  it("navigates home when 'Analyze Another' is clicked", async () => {
    mockGet.mockResolvedValueOnce({ data: fakeResult });
    renderWithRoute("/results?id=result-123");

    await waitFor(() => screen.getByText("Analyze Another"));
    fireEvent.click(screen.getByText("Analyze Another"));
    expect(mockNavigate).toHaveBeenCalledWith("/");
  });

  it("renders experience and education", async () => {
    mockGet.mockResolvedValueOnce({ data: fakeResult });
    renderWithRoute("/results?id=result-123");

    await waitFor(() => screen.getByText("Senior Engineer"));
    expect(screen.getByText(/Acme/)).toBeInTheDocument();
    expect(screen.getByText("BS Computer Science")).toBeInTheDocument();
  });
});
