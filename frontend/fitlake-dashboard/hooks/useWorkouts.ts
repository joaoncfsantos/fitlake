import useSWR from "swr";

import { useDemoMode } from "@/contexts/demo-mode";
import { workoutsDemoData } from "@/data/workouts-demo-data";

const fetcher = (url: string) =>
  fetch(url, {
    headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
  }).then((r) => r.json());

export interface WorkoutSummary {
  id: number;
  platform: string;
  external_id: string;
  title: string;
  start_time: string;
  duration_seconds: number;
  exercise_count: number;
  created_at: string;
}

export interface WorkoutsResponse {
  items: WorkoutSummary[];
  total: number;
  skip: number;
  limit: number;
}

export function useWorkouts(limit = 50) {
  const { isDemo } = useDemoMode();

  const { data, error, isLoading, mutate } = useSWR<WorkoutsResponse>(
    isDemo ? null : `/api/v1/workouts?limit=${limit}`,
    fetcher,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    },
  );

  if (isDemo) {
    return {
      data: workoutsDemoData.items.slice(0, limit) as WorkoutSummary[],
      loading: false,
      error: null,
      refetch: () => {},
    };
  }

  return {
    data: data?.items || [],
    loading: isLoading,
    error,
    refetch: mutate,
  };
}
