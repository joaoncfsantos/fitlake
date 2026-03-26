import useSWR from "swr";

import { useDemoMode } from "@/contexts/demo-mode";
import { getDemoActivityDetail } from "@/data/running-demo-data";
import type { ActivityDetail } from "@/lib/activity-types";

export type { ActivityDetail } from "@/lib/activity-types";

const fetcher = (url: string) =>
  fetch(url, {
    headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
  }).then((r) => {
    if (!r.ok) throw new Error(r.statusText || "Failed to load activity");
    return r.json();
  });

export function useActivityDetail(activityId: number | null) {
  const { isDemo } = useDemoMode();

  const { data, error, isLoading } = useSWR<ActivityDetail>(
    activityId !== null && !isDemo ? `/api/v1/activities/${activityId}` : null,
    fetcher,
    { revalidateOnFocus: false },
  );

  if (isDemo && activityId !== null) {
    return {
      data: getDemoActivityDetail(activityId),
      loading: false,
      error: null as Error | null,
    };
  }

  return {
    data: data ?? null,
    loading: isLoading,
    error: error as Error | null,
  };
}
