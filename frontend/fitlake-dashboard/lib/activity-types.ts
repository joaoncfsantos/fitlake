/** Full activity payload from GET /api/v1/activities/{id} (same shape as list items). */
export interface ActivityDetail {
  id: number;
  platform: string;
  external_id: string;
  name: string;
  activity_type: string;
  sport_type?: string | null;
  start_date: string;
  elapsed_time_seconds: number;
  moving_time_seconds?: number | null;
  distance_meters?: number | null;
  average_speed_mps?: number | null;
  max_speed_mps?: number | null;
  total_elevation_gain_meters?: number | null;
  elevation_high_meters?: number | null;
  elevation_low_meters?: number | null;
  average_heartrate?: number | null;
  max_heartrate?: number | null;
  average_watts?: number | null;
  max_watts?: number | null;
  calories?: number | null;
  description?: string | null;
  created_at: string;
  updated_at: string;
}
