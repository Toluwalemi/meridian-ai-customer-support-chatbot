import { SignedIn, SignedOut, SignIn } from "@clerk/clerk-react";

import { ChatPage } from "@/features/chat/ChatPage";

type Props = {
  clerkEnabled: boolean;
};

function AuthDisabledLanding() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
      <div className="w-full max-w-xl space-y-6 rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="space-y-2 text-center">
          <h1 className="text-2xl font-semibold text-slate-900">Meridian Support</h1>
          <p className="text-sm text-slate-600">
            The frontend is running, but Clerk is not configured yet.
          </p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
          Add a real <code>VITE_CLERK_PUBLISHABLE_KEY</code> in <code>frontend/.env</code> to
          enable sign-in.
        </div>
      </div>
    </div>
  );
}

export default function App({ clerkEnabled }: Props) {
  if (!clerkEnabled) {
    return <AuthDisabledLanding />;
  }

  return (
    <>
      <SignedIn>
        <ChatPage />
      </SignedIn>
      <SignedOut>
        <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4">
          <div className="w-full max-w-md space-y-6">
            <div className="text-center">
              <h1 className="text-2xl font-semibold text-slate-900">Meridian Support</h1>
              <p className="mt-2 text-sm text-slate-600">
                Sign in to chat with our support assistant.
              </p>
            </div>
            <div className="flex justify-center">
              <SignIn routing="hash" />
            </div>
          </div>
        </div>
      </SignedOut>
    </>
  );
}
