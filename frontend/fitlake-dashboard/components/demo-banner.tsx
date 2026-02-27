"use client";

import { useAuth } from "@clerk/nextjs";
import { SignInDialog } from "./sign-in-dialog";

export function DemoBanner() {
  const { isSignedIn, isLoaded } = useAuth();

  if (!isLoaded) return null;
  if (!isSignedIn) {
    return (
      <div className="sticky top-0 w-full z-5 bg-yellow-950 border-b border-yellow-800 text-yellow-400 text-xs text-center py-1.5 font-mono">
        Viewing demo data — sign in to see your own data
        <SignInDialog
          trigger={<button className="ml-4 underline">Sign in</button>}
        />
      </div>
    );
  }

  return <></>;
}
