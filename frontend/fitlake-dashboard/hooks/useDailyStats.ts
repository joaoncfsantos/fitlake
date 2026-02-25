import useSWR from "swr";
import { useDemoMode } from "@/contexts/demo-mode";
import { dailyStatsDemoData } from "@/data/daily-stats-demo-data";

const fetcher = (url: string) =>
  fetch(url, {
    headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
  }).then((r) => r.json());
export function useDailyStats(limit = 30) {
  const { isDemo } = useDemoMode();

  const { data, error, isLoading, mutate } = useSWR(
    isDemo ? null : `/api/v1/daily-stats?limit=${limit}`,
    fetcher,
    { revalidateOnFocus: false, dedupingInterval: 60000 },
  );

  if (isDemo) {
    const items = [...dailyStatsDemoData.items].reverse().slice(0, limit);
    return { data: items, loading: false, error: null, refetch: () => {} };
  }

  return {
    data: data?.items ? [...data.items].reverse() : [],
    loading: isLoading,
    error,
    refetch: mutate,
  };
}
