import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { HomePage } from "../../pages/HomePage";
import apiClient from "../../api/client";

vi.mock("../../api/client", () => ({
  default: { post: vi.fn(), get: vi.fn() },
}));

// Mock useNavigate so we can track navigation
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockPost = vi.mocked(apiClient.post);

afterEach(() => {
  vi.clearAllMocks();
});

function renderHomePage() {
  return render(
    <MemoryRouter>
      <HomePage />
    </MemoryRouter>
  );
}

describe("HomePage", () => {
  it("renders the main heading", () => {
    renderHomePage();
    expect(screen.getByText("Resume Analyzer")).toBeInTheDocument();
  });

  it("submit button is disabled initially", () => {
    renderHomePage();
    const btn = screen.getByRole("button", { name: /Analyze Resume/i });
    expect(btn).toBeDisabled();
  });

  it("navigates to /history when View History is clicked", () => {
    renderHomePage();
    fireEvent.click(screen.getByRole("button", { name: /View History/i }));
    expect(mockNavigate).toHaveBeenCalledWith("/history");
  });

  it("submit button remains disabled with job description under 50 chars", async () => {
    renderHomePage();
    const textarea = screen.getByPlaceholderText(/Paste the full job description/i);
    fireEvent.change(textarea, { target: { value: "Short description" } });
    const btn = screen.getByRole("button", { name: /Analyze Resume/i });
    expect(btn).toBeDisabled();
  });

  it("shows upload error when API call fails", async () => {
    mockPost.mockRejectedValueOnce(new Error("Upload failed"));

    renderHomePage();
    const dropzone = screen.getByText(/Drag & drop your resume PDF/i).closest("div")!.parentElement!;
    const input = dropzone.querySelector("input[type='file']") as HTMLInputElement;

    const file = new File(["content"], "resume.pdf", { type: "application/pdf" });
    Object.defineProperty(input, "files", { value: [file] });
    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file], types: ["Files"] },
    });

    await waitFor(() => {
      expect(screen.getByText("Upload failed")).toBeInTheDocument();
    });
  });

  it("shows success message after upload and navigates to results", async () => {
    mockPost
      .mockResolvedValueOnce({
        data: {
          upload_url: "https://s3.example.com",
          upload_fields: {},
          s3_key: "uploads/abc/resume.pdf",
          expires_in: 300,
        },
      })
      .mockResolvedValueOnce({
        data: {
          id: "result-123",
          overall_score: 78,
          categories: [],
          skills: [],
          experience: [],
          education: [],
          suggestions: [],
          created_at: "2026-04-17T10:00:00Z",
          file_name: "resume.pdf",
          job_description: "A long job description for the Python developer role",
        },
      });

    const mockXhrInstance = {
      open: vi.fn(),
      upload: { onprogress: null as unknown },
      onload: null as (() => void) | null,
      onerror: null as (() => void) | null,
      status: 200,
      send: vi.fn(function (this: { onload: (() => void) | null }) {
        const self = this;
        Promise.resolve().then(() => { if (self.onload) self.onload(); });
      }),
    };
    vi.stubGlobal("XMLHttpRequest", function () { return mockXhrInstance; });

    renderHomePage();

    const dropzone = screen.getByText(/Drag & drop your resume PDF/i).closest("div")!.parentElement!;
    const file = new File(["content"], "resume.pdf", { type: "application/pdf" });

    fireEvent.drop(dropzone, {
      dataTransfer: { files: [file], types: ["Files"] },
    });

    await waitFor(() =>
      expect(screen.getByText("Resume uploaded successfully")).toBeInTheDocument()
    );

    const textarea = screen.getByPlaceholderText(/Paste the full job description/i);
    fireEvent.change(textarea, {
      target: { value: "A long job description for the Python developer role with 50+ chars" },
    });

    const btn = screen.getByRole("button", { name: /Analyze Resume/i });
    await waitFor(() => expect(btn).not.toBeDisabled());
    fireEvent.click(btn);

    await waitFor(() =>
      expect(mockNavigate).toHaveBeenCalledWith("/results?id=result-123")
    );
  });
});
