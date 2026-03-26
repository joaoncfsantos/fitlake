import useSWR from "swr";

import { useDemoMode } from "@/contexts/demo-mode";
import { getDemoWorkoutDetail } from "@/data/workouts-demo-data";
import type { WorkoutDetail } from "@/lib/workout-types";

export type {
  WorkoutDetail,
  WorkoutExercise,
  WorkoutSet,
} from "@/lib/workout-types";

const fetcher = (url: string) =>
  fetch(url, {
    headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
  }).then((r) => {
    if (!r.ok) throw new Error(r.statusText || "Failed to load workout");
    return r.json();
  });

export function useWorkoutDetail(workoutId: number | null) {
  const { isDemo } = useDemoMode();

  const { data, error, isLoading } = useSWR<WorkoutDetail>(
    workoutId !== null && !isDemo ? `/api/v1/workouts/${workoutId}` : null,
    fetcher,
    { revalidateOnFocus: false },
  );

  if (isDemo && workoutId !== null) {
    return {
      data: getDemoWorkoutDetail(workoutId),
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
