import { ToolCallTrace } from "./types";
import { ToolCallNotice } from "./ToolCallNotice";

type Props = {
  role: "user" | "assistant";
  content: string;
  toolCalls?: ToolCallTrace[];
};

export function MessageBubble({ role, content, toolCalls }: Props) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] space-y-2 rounded-lg border px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "border-slate-900 bg-slate-900 text-white"
            : "border-slate-200 bg-white text-slate-900"
        }`}
      >
        <p className="whitespace-pre-wrap">{content}</p>
        {!isUser && toolCalls && toolCalls.length > 0 && (
          <div className="space-y-1 pt-1">
            {toolCalls.map((c, i) => (
              <ToolCallNotice key={`${c.name}-${i}`} call={c} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
