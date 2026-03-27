import useSWR from "swr";

import { useDemoMode } from "@/contexts/demo-mode";
import { getDemoWorkoutDetail } from "@/data/workouts-demo-data";
import type { WorkoutDetail } from "@/lib/workout-types";

export type {
  WorkoutDetail,
  WorkoutExercise,
  WorkoutMuscleDistributionItem,
  WorkoutSet,
} from "@/lib/workout-types";

/** Older API responses or caches may omit new fields — keep UI safe. */
function normalizeWorkoutDetail(raw: Record<string, unknown>): WorkoutDetail {
  const base = raw as unknown as WorkoutDetail;
  return {
    ...base,
    exercises: Array.isArray(raw.exercises) ? base.exercises : [],
    muscle_distribution: Array.isArray(raw.muscle_distribution)
      ? base.muscle_distribution
      : [],
    total_sets: typeof raw.total_sets === "number" ? raw.total_sets : 0,
  };
}

const fetcher = (url: string) =>
  fetch(url, {
    headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
  })
    .then((r) => {
      if (!r.ok) throw new Error(r.statusText || "Failed to load workout");
      return r.json();
    })
    .then((data) => normalizeWorkoutDetail(data as Record<string, unknown>));

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
