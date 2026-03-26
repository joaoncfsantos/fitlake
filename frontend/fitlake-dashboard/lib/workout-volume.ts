import type { WorkoutExercise, WorkoutSet } from "@/lib/workout-types";

/**
 * Volume for one set: weight (kg) × reps. Missing values contribute 0.
 */
export function setVolumeKg(set: WorkoutSet): number {
  const w = set.weight_kg;
  const r = set.reps;
  if (w == null || r == null || Number.isNaN(w) || Number.isNaN(r)) return 0;
  return w * r;
}

/** Sum of set volumes for one exercise. */
export function exerciseVolumeKg(exercise: WorkoutExercise): number {
  const sets = exercise.sets ?? [];
  return sets.reduce((sum, s) => sum + setVolumeKg(s), 0);
}

/** Total volume for a workout (all exercises). */
export function workoutVolumeKg(exercises: WorkoutExercise[]): number {
  return exercises.reduce((sum, ex) => sum + exerciseVolumeKg(ex), 0);
}
