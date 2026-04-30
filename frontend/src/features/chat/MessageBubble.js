import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { ToolCallNotice } from "./ToolCallNotice";
export function MessageBubble({ role, content, toolCalls }) {
    const isUser = role === "user";
    return (_jsx("div", { className: `flex ${isUser ? "justify-end" : "justify-start"}`, children: _jsxs("div", { className: `max-w-[85%] space-y-2 rounded-lg border px-4 py-3 text-sm leading-relaxed ${isUser
                ? "border-slate-900 bg-slate-900 text-white"
                : "border-slate-200 bg-white text-slate-900"}`, children: [_jsx("p", { className: "whitespace-pre-wrap", children: content }), !isUser && toolCalls && toolCalls.length > 0 && (_jsx("div", { className: "space-y-1 pt-1", children: toolCalls.map((c, i) => (_jsx(ToolCallNotice, { call: c }, `${c.name}-${i}`))) }))] }) }));
}
