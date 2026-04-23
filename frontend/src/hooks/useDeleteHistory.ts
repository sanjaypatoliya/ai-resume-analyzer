import { useMutation, useQueryClient } from "@tanstack/react-query";
import apiClient from "../api/client";

export function useDeleteHistory() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (ids: string[]) => {
      await Promise.all(ids.map((id) => apiClient.delete(`/history/${id}`)));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["history"] });
    },
  });
}
