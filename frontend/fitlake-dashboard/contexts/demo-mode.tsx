"use client";

import { createContext, useContext } from "react";
import { useAuth } from "@clerk/nextjs";

type DemoModeContextType = {
  isDemo: boolean;
};

const DemoModeContext = createContext<DemoModeContextType>({
  isDemo: false,
});

export function DemoModeProvider({ children }: { children: React.ReactNode }) {
  const { isSignedIn, isLoaded } = useAuth();

  const isDemo = isLoaded ? !isSignedIn : false;

  return (
    <DemoModeContext.Provider value={{ isDemo }}>
      {children}
    </DemoModeContext.Provider>
  );
}

export const useDemoMode = () => useContext(DemoModeContext);
