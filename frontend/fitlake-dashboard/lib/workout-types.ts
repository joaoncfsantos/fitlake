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
  sets?: WorkoutSet[];
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
}
