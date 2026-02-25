"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";

type DemoModeContextType = {
  isDemo: boolean;
  enableDemo: () => void;
  disableDemo: () => void;
};

const DemoModeContext = createContext<DemoModeContextType>({
  isDemo: false,
  enableDemo: () => {},
  disableDemo: () => {},
});

export function DemoModeProvider({ children }: { children: React.ReactNode }) {
  const [manualDemo, setManualDemo] = useState(false);
  const { isSignedIn, isLoaded } = useAuth();

  useEffect(() => {
    setManualDemo(sessionStorage.getItem("fitlake-demo") === "true");
  }, []);

  // isDemo is true when: manually enabled, not signed in, or Clerk hasn't loaded yet
  const isDemo = manualDemo || !isSignedIn || !isLoaded;

  const enableDemo = () => {
    sessionStorage.setItem("fitlake-demo", "true");
    setManualDemo(true);
  };
  const disableDemo = () => {
    sessionStorage.removeItem("fitlake-demo");
    setManualDemo(false);
  };

  return (
    <DemoModeContext.Provider value={{ isDemo, enableDemo, disableDemo }}>
      {children}
    </DemoModeContext.Provider>
  );
}

export const useDemoMode = () => useContext(DemoModeContext);
