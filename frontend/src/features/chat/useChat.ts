import { useAuth } from "@clerk/clerk-react";
import { useMutation } from "@tanstack/react-query";
import { useMemo } from "react";

import { createApiClient } from "@/lib/api";
import { ChatMessage, ChatResponse, ChatResponseSchema } from "./types";

export function useSendChat() {
  const { getToken } = useAuth();
  const api = useMemo(() => createApiClient(() => getToken()), [getToken]);

  return useMutation({
    mutationFn: async (messages: ChatMessage[]): Promise<ChatResponse> => {
      const { data } = await api.post("/chat", { messages });
      return ChatResponseSchema.parse(data);
    },
  });
}
