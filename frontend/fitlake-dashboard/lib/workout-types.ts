/** One set as stored from Hevy (JSON in DB). */
export interface WorkoutSet {
  index?: number;
  type?: string;
  weight_kg?: number | null;
  reps?: number | null;
  distance_meters?: number | null;
  duration_seconds?: number | null;
  rpe?: number | null;
}

export interface WorkoutExercise {
  title?: string;
  index?: number;
  exercise_template_id?: string;
  sets?: WorkoutSet[];
}

/** Per muscle group (same weighting as analytics: primary 1×, secondary 0.5×). */
export interface WorkoutMuscleDistributionItem {
  muscle_group: string;
  weighted_sets: number;
  percentage: number;
  total_sets: number;
}

export interface WorkoutDetail {
  id: number;
  platform: string;
  external_id: string;
  title: string;
  description?: string | null;
  start_time: string;
  end_time: string;
  duration_seconds: number;
  exercises: WorkoutExercise[];
  created_at: string;
  updated_at: string;
  /** Total number of logged sets (all exercises). */
  total_sets: number;
  /** Muscles targeted in this session; empty if templates are missing. */
  muscle_distribution: WorkoutMuscleDistributionItem[];
}
