"use client";

import { useDemoMode } from "@/contexts/demo-mode";
import { useRouter } from "next/navigation";

export function DemoBanner() {
  const { isDemo, disableDemo } = useDemoMode();
  const router = useRouter();

  if (!isDemo) return null;

  const handleDemo = () => {
    if (isDemo) {
      disableDemo();
      router.push("/");
    }
  };

  return (
    <div className="bg-yellow-500/10 border-b border-yellow-500/20 text-yellow-400 text-xs text-center py-1.5 font-mono">
      Demo mode — viewing sample data
      <button onClick={handleDemo} className="ml-4 underline">
        Exit
      </button>
    </div>
  );
}
