import { jsx as _jsx } from "react/jsx-runtime";
import { ClerkProvider } from "@clerk/clerk-react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { env, hasValidClerkPublishableKey } from "./lib/env";
import "./index.css";
const queryClient = new QueryClient({
    defaultOptions: {
        queries: { retry: 1, staleTime: 30_000 },
    },
});
const rootEl = document.getElementById("root");
if (!rootEl) {
    throw new Error("Root element #root not found");
}
const clerkPublishableKey = hasValidClerkPublishableKey(env.VITE_CLERK_PUBLISHABLE_KEY)
    ? env.VITE_CLERK_PUBLISHABLE_KEY
    : null;
const clerkEnabled = clerkPublishableKey !== null;
createRoot(rootEl).render(_jsx(StrictMode, { children: clerkEnabled ? (_jsx(ClerkProvider, { publishableKey: clerkPublishableKey, children: _jsx(QueryClientProvider, { client: queryClient, children: _jsx(App, { clerkEnabled: clerkEnabled }) }) })) : (_jsx(QueryClientProvider, { client: queryClient, children: _jsx(App, { clerkEnabled: clerkEnabled }) })) }));
