import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
export function Composer({ disabled, onSubmit }) {
    const [value, setValue] = useState("");
    const send = () => {
        const trimmed = value.trim();
        if (!trimmed || disabled)
            return;
        onSubmit(trimmed);
        setValue("");
    };
    const handleSubmit = (event) => {
        event.preventDefault();
        send();
    };
    const handleKeyDown = (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            send();
        }
    };
    return (_jsxs("form", { onSubmit: handleSubmit, className: "flex items-end gap-2 border-t border-slate-200 bg-white p-3", children: [_jsx("textarea", { value: value, onChange: (e) => setValue(e.target.value), onKeyDown: handleKeyDown, placeholder: "Ask about products, orders, or returns...", rows: 2, className: "min-h-[44px] flex-1 resize-y rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-slate-900 focus:outline-none", disabled: disabled }), _jsx("button", { type: "submit", disabled: disabled || !value.trim(), className: "h-[44px] rounded-md border border-slate-900 bg-slate-900 px-4 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50", children: "Send" })] }));
}
