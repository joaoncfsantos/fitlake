import useSWR from "swr";

export interface InsightResponse {
  insight: string;
  period_start: string;
  period_end: string;
}

const fetcher = (url: string) =>
  fetch(url, {
    headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
  }).then((r) => r.json());

export function useInsight() {
  // fetch, return { data, loading, error }
  const { data, error, isLoading } = useSWR<InsightResponse>(
    "/api/v1/insight",
    fetcher,
  );
  return { data, error, isLoading };
}
