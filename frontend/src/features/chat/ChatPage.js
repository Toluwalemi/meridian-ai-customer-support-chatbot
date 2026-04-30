import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { UserButton } from "@clerk/clerk-react";
import { useEffect, useRef, useState } from "react";
import { Composer } from "./Composer";
import { MessageBubble } from "./MessageBubble";
import { useSendChat } from "./useChat";
const GREETING = {
    role: "assistant",
    content: "Hi, I'm Meridian's support assistant. I can help you browse products, check stock, look up your orders, or place a new one. What can I do for you?",
    toolCalls: [],
};
export function ChatPage() {
    const [turns, setTurns] = useState([GREETING]);
    const [error, setError] = useState(null);
    const send = useSendChat();
    const scrollRef = useRef(null);
    useEffect(() => {
        scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
    }, [turns, send.isPending]);
    const handleSubmit = async (text) => {
        setError(null);
        const userTurn = { role: "user", content: text };
        const next = [...turns, userTurn];
        setTurns(next);
        const payload = next.map((t) => ({ role: t.role, content: t.content }));
        try {
            const response = await send.mutateAsync(payload);
            setTurns((prev) => [
                ...prev,
                { role: "assistant", content: response.reply, toolCalls: response.tool_calls },
            ]);
        }
        catch (err) {
            const message = err instanceof Error ? err.message : "Something went wrong";
            setError(message);
        }
    };
    return (_jsxs("div", { className: "flex h-full flex-col bg-slate-50", children: [_jsxs("header", { className: "flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3", children: [_jsxs("div", { children: [_jsx("h1", { className: "text-base font-semibold text-slate-900", children: "Meridian Support" }), _jsx("p", { className: "text-xs text-slate-500", children: "Powered by Claude Haiku and the Meridian MCP" })] }), _jsx(UserButton, { afterSignOutUrl: "/" })] }), _jsx("div", { ref: scrollRef, className: "flex-1 overflow-y-auto px-6 py-4", children: _jsxs("div", { className: "mx-auto flex max-w-2xl flex-col gap-4", children: [turns.map((turn, i) => (_jsx(MessageBubble, { role: turn.role, content: turn.content, ...("toolCalls" in turn ? { toolCalls: turn.toolCalls } : {}) }, i))), send.isPending && (_jsx("div", { className: "text-xs text-slate-500", children: "Assistant is thinking..." })), error && (_jsx("div", { className: "rounded border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-700", children: error }))] }) }), _jsx("div", { className: "mx-auto w-full max-w-2xl", children: _jsx(Composer, { disabled: send.isPending, onSubmit: handleSubmit }) })] }));
}
