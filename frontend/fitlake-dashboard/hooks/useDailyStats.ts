import useSWR from 'swr'

const fetcher = (url: string) => 
  fetch(url, {
    headers: { 'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || '' }
  }).then(r => r.json())

export function useDailyStats(limit = 30) {
  const { data, error, isLoading, mutate } = useSWR(
    `/api/v1/daily-stats?limit=${limit}`,
    fetcher,
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute
    }
  )
  
  return {
    data: data?.items ? [...data.items].reverse() : [],
    loading: isLoading,
    error,
    refetch: mutate
  }
}