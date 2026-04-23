import { useQuery } from "@tanstack/react-query";
import apiClient from "../api/client";
import type { HistoryResponse } from "../types";

export function useHistory(limit = 20) {
  return useQuery<HistoryResponse>({
    queryKey: ["history", limit],
    queryFn: async () => {
      const { data } = await apiClient.get<HistoryResponse>("/history", {
        params: { limit },
      });
      return data;
    },
  });
}
