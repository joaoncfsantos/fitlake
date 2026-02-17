import useSWR from "swr";

const fetcher = (url: string) =>
  fetch(url, {
    headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
  }).then((r) => r.json());

export interface MuscleDistributionItem {
  muscle_group: string;
  weighted_sets: number;
  percentage: number;
  total_sets: number;
}

export interface MuscleDistributionResponse {
  muscle_distribution: MuscleDistributionItem[];
  total_sets: number;
  total_workouts: number;
  primary_muscle_weight: number;
  secondary_muscle_weight: number;
}

export function useMuscleDistribution(limit = 1000) {
  const { data, error, isLoading, mutate } = useSWR<MuscleDistributionResponse>(
    `/api/v1/workouts/muscle-distribution?limit=${limit}`,
    fetcher,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute
    },
  );

  return {
    data: data || null,
    loading: isLoading,
    error,
    refetch: mutate,
  };
}
