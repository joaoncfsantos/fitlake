"use client";

/* import { useDemoMode } from "@/contexts/demo-mode"; */
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import { SignInDialog } from "./sign-in-dialog";

export function DemoBanner() {
  /* const { isDemo, disableDemo } = useDemoMode(); */
  const { isSignedIn } = useAuth();
  /* const router = useRouter(); */

  /*  if (!isDemo) return null; */

  if (!isSignedIn) {
    return (
      <div className="fixed top-0 left-0 right-0 bg-yellow-950 border-b border-yellow-800 text-yellow-400 text-xs text-center py-1.5 font-mono">
        Viewing demo data — sign in to see your own data
        <SignInDialog
          trigger={<button className="ml-4 underline">Sign in</button>}
        />
      </div>
    );
  }

  /*  const handleExitDemo = () => {
    disableDemo();
    router.push("/");
  }; */

  return (
    /*     <div className="bg-yellow-500/10 border-b border-yellow-500/20 text-yellow-400 text-xs text-center py-1.5 font-mono">
      Demo mode — viewing sample data
      <button onClick={handleExitDemo} className="ml-4 underline">
        Exit
      </button>
    </div> */
    <></>
  );
}
