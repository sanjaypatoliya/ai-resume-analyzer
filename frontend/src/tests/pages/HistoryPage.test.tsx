import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { createElement } from "react";
import { HistoryPage } from "../../pages/HistoryPage";
import apiClient from "../../api/client";
import type { HistoryResponse } from "../../types";

vi.mock("../../api/client", () => ({
  default: { post: vi.fn(), get: vi.fn() },
}));

const mockNavigate = vi.fn();
vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return { ...actual, useNavigate: () => mockNavigate };
});

const mockGet = vi.mocked(apiClient.get);

function renderHistoryPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    createElement(
      QueryClientProvider,
      { client: queryClient },
      createElement(
        MemoryRouter,
        null,
        createElement(HistoryPage)
      )
    )
  );
}

afterEach(() => vi.clearAllMocks());

describe("HistoryPage", () => {
  it("shows loading spinner while fetching", () => {
    mockGet.mockReturnValueOnce(new Promise(() => {}));
    renderHistoryPage();
    expect(document.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("shows error message when fetch fails", async () => {
    mockGet.mockRejectedValueOnce(new Error("Network error"));
    renderHistoryPage();

    await waitFor(() =>
      expect(screen.getByText(/Failed to load history/i)).toBeInTheDocument()
    );
  });

  it("shows empty state when no history", async () => {
    mockGet.mockResolvedValueOnce({ data: { items: [], total: 0 } satisfies HistoryResponse });
    renderHistoryPage();

    await waitFor(() =>
      expect(screen.getByText("No analyses yet")).toBeInTheDocument()
    );
  });

  it("renders history items", async () => {
    const data: HistoryResponse = {
      items: [
        { id: "abc", file_name: "resume.pdf", overall_score: 78, created_at: "2026-04-17T10:00:00Z" },
        { id: "def", file_name: "cv.pdf", overall_score: 45, created_at: "2026-04-16T08:00:00Z" },
      ],
      total: 2,
    };
    mockGet.mockResolvedValueOnce({ data });
    renderHistoryPage();

    await waitFor(() => screen.getByText("resume.pdf"));
    expect(screen.getByText("cv.pdf")).toBeInTheDocument();
    expect(screen.getByText("2 results")).toBeInTheDocument();
  });

  it("shows score labels based on score range", async () => {
    const data: HistoryResponse = {
      items: [
        { id: "a", file_name: "good.pdf", overall_score: 80, created_at: "2026-04-17T10:00:00Z" },
        { id: "b", file_name: "partial.pdf", overall_score: 55, created_at: "2026-04-17T09:00:00Z" },
        { id: "c", file_name: "low.pdf", overall_score: 30, created_at: "2026-04-17T08:00:00Z" },
      ],
      total: 3,
    };
    mockGet.mockResolvedValueOnce({ data });
    renderHistoryPage();

    await waitFor(() => screen.getByText("Good Match"));
    expect(screen.getByText("Partial Match")).toBeInTheDocument();
    expect(screen.getByText("Low Match")).toBeInTheDocument();
  });

  it("navigates to results when a history item is clicked", async () => {
    const data: HistoryResponse = {
      items: [
        { id: "abc", file_name: "resume.pdf", overall_score: 78, created_at: "2026-04-17T10:00:00Z" },
      ],
      total: 1,
    };
    mockGet.mockResolvedValueOnce({ data });
    renderHistoryPage();

    await waitFor(() => screen.getByText("resume.pdf"));
    fireEvent.click(screen.getByRole("button", { name: /view/i }));
    expect(mockNavigate).toHaveBeenCalledWith("/results?id=abc");
  });

  it("navigates home when 'Analyze Resume' is clicked", async () => {
    mockGet.mockResolvedValueOnce({ data: { items: [], total: 0 } });
    renderHistoryPage();

    await waitFor(() => screen.getAllByRole("button", { name: /Analyze Resume/i }));
    fireEvent.click(screen.getAllByRole("button", { name: /Analyze Resume/i })[0]);
    expect(mockNavigate).toHaveBeenCalledWith("/");
  });
});
