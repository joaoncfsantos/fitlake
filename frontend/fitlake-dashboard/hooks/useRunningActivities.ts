import useSWR from "swr";

const fetcher = (url: string) =>
  fetch(url, {
    headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
  }).then((r) => r.json());

export interface RunningActivity {
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
  average_heartrate?: number | null;
  max_heartrate?: number | null;
  calories?: number | null;
  created_at: string;
  updated_at: string;
}

export interface RunningActivitiesResponse {
  items: RunningActivity[];
  total: number;
  skip: number;
  limit: number;
}

export function useRunningActivities(limit = 50) {
  const { data, error, isLoading, mutate } = useSWR<RunningActivitiesResponse>(
    `/api/v1/activities?activity_type=Run&limit=${limit}`,
    fetcher,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute
    },
  );

  return {
    data: data?.items || [],
    loading: isLoading,
    error,
    refetch: mutate,
  };
}
