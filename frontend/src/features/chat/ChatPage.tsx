import { UserButton } from "@clerk/clerk-react";
import { useEffect, useRef, useState } from "react";

import { Composer } from "./Composer";
import { MessageBubble } from "./MessageBubble";
import { ChatMessage, ToolCallTrace } from "./types";
import { useSendChat } from "./useChat";

type AssistantTurn = ChatMessage & {
  role: "assistant";
  toolCalls: ToolCallTrace[];
};

type Turn = ChatMessage | AssistantTurn;

const GREETING: AssistantTurn = {
  role: "assistant",
  content:
    "Hi, I'm Meridian's support assistant. I can help you browse products, check stock, look up your orders, or place a new one. What can I do for you?",
  toolCalls: [],
};

export function ChatPage() {
  const [turns, setTurns] = useState<Turn[]>([GREETING]);
  const [error, setError] = useState<string | null>(null);
  const send = useSendChat();
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [turns, send.isPending]);

  const handleSubmit = async (text: string) => {
    setError(null);
    const userTurn: ChatMessage = { role: "user", content: text };
    const next: Turn[] = [...turns, userTurn];
    setTurns(next);

    const payload: ChatMessage[] = next.map((t) => ({ role: t.role, content: t.content }));

    try {
      const response = await send.mutateAsync(payload);
      setTurns((prev) => [
        ...prev,
        { role: "assistant", content: response.reply, toolCalls: response.tool_calls },
      ]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong";
      setError(message);
    }
  };

  return (
    <div className="flex h-full flex-col bg-slate-50">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
        <div>
          <h1 className="text-base font-semibold text-slate-900">Meridian Support</h1>
          <p className="text-xs text-slate-500">Powered by Claude Haiku and the Meridian MCP</p>
        </div>
        <UserButton afterSignOutUrl="/" />
      </header>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-4">
        <div className="mx-auto flex max-w-2xl flex-col gap-4">
          {turns.map((turn, i) => (
            <MessageBubble
              key={i}
              role={turn.role}
              content={turn.content}
              {...("toolCalls" in turn ? { toolCalls: turn.toolCalls } : {})}
            />
          ))}
          {send.isPending && (
            <div className="text-xs text-slate-500">Assistant is thinking...</div>
          )}
          {error && (
            <div className="rounded border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700">
              {error}
            </div>
          )}
        </div>
      </div>

      <div className="mx-auto w-full max-w-2xl">
        <Composer disabled={send.isPending} onSubmit={handleSubmit} />
      </div>
    </div>
  );
}
