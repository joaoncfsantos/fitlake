import { useState, useCallback } from "react";

export interface InsightResponse {
  insight: string;
  period_start: string;
  period_end: string;
}

export function useInsight() {
  const [data, setData] = useState<InsightResponse | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const trigger = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/v1/insight", {
        headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
      });
      const json = await res.json();
      setData(json);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { data, error, isLoading, trigger };
}
