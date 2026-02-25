"use client";

import { createContext, useContext, useState, useEffect } from "react";

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
  const [isDemo, setIsDemo] = useState(false);

  // Persist across page navigations using sessionStorage
  useEffect(() => {
    setIsDemo(sessionStorage.getItem("fitlake-demo") === "true");
  }, []);

  const enableDemo = () => {
    sessionStorage.setItem("fitlake-demo", "true");
    setIsDemo(true);
  };

  const disableDemo = () => {
    sessionStorage.removeItem("fitlake-demo");
    setIsDemo(false);
  };

  return (
    <DemoModeContext.Provider value={{ isDemo, enableDemo, disableDemo }}>
      {children}
    </DemoModeContext.Provider>
  );
}

export const useDemoMode = () => useContext(DemoModeContext);
