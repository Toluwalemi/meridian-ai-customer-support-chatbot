import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from "react/jsx-runtime";
import { SignedIn, SignedOut, SignIn } from "@clerk/clerk-react";
import { ChatPage } from "@/features/chat/ChatPage";
function AuthDisabledLanding() {
    return (_jsx("div", { className: "flex min-h-screen items-center justify-center bg-slate-50 px-4", children: _jsxs("div", { className: "w-full max-w-xl space-y-6 rounded-xl border border-slate-200 bg-white p-8 shadow-sm", children: [_jsxs("div", { className: "space-y-2 text-center", children: [_jsx("h1", { className: "text-2xl font-semibold text-slate-900", children: "Meridian Support" }), _jsx("p", { className: "text-sm text-slate-600", children: "The frontend is running, but Clerk is not configured yet." })] }), _jsxs("div", { className: "rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700", children: ["Add a real ", _jsx("code", { children: "VITE_CLERK_PUBLISHABLE_KEY" }), " in ", _jsx("code", { children: "frontend/.env" }), " to enable sign-in."] })] }) }));
}
export default function App({ clerkEnabled }) {
    if (!clerkEnabled) {
        return _jsx(AuthDisabledLanding, {});
    }
    return (_jsxs(_Fragment, { children: [_jsx(SignedIn, { children: _jsx(ChatPage, {}) }), _jsx(SignedOut, { children: _jsx("div", { className: "flex min-h-screen items-center justify-center bg-slate-50 px-4", children: _jsxs("div", { className: "w-full max-w-md space-y-6", children: [_jsxs("div", { className: "text-center", children: [_jsx("h1", { className: "text-2xl font-semibold text-slate-900", children: "Meridian Support" }), _jsx("p", { className: "mt-2 text-sm text-slate-600", children: "Sign in to chat with our support assistant." })] }), _jsx("div", { className: "flex justify-center", children: _jsx(SignIn, { routing: "hash" }) })] }) }) })] }));
}
