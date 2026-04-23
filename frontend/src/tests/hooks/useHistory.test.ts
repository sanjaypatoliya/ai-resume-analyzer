import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createElement } from "react";
import { useHistory } from "../../hooks/useHistory";
import apiClient from "../../api/client";
import type { HistoryResponse } from "../../types";

vi.mock("../../api/client", () => ({
  default: { post: vi.fn(), get: vi.fn() },
}));

const mockGet = vi.mocked(apiClient.get);

function wrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return createElement(QueryClientProvider, { client: queryClient }, children);
}

const fakeHistory: HistoryResponse = {
  items: [
    { id: "abc", file_name: "resume.pdf", overall_score: 78, created_at: "2026-04-17T10:00:00Z" },
  ],
  total: 1,
};

afterEach(() => vi.restoreAllMocks());

describe("useHistory", () => {
  it("fetches history and returns data", async () => {
    mockGet.mockResolvedValueOnce({ data: fakeHistory });

    const { result } = renderHook(() => useHistory(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(fakeHistory);
    expect(mockGet).toHaveBeenCalledWith("/history", { params: { limit: 20 } });
  });

  it("returns error state when fetch fails", async () => {
    mockGet.mockRejectedValueOnce(new Error("Network error"));

    const { result } = renderHook(() => useHistory(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
    expect(result.current.data).toBeUndefined();
  });

  it("accepts custom limit parameter", async () => {
    mockGet.mockResolvedValueOnce({ data: { items: [], total: 0 } });

    const { result } = renderHook(() => useHistory(5), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockGet).toHaveBeenCalledWith("/history", { params: { limit: 5 } });
  });
});
