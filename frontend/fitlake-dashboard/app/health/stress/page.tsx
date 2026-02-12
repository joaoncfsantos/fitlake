"use client"

import { useEffect, useState } from "react"
import { PageLayout } from "@/components/page-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { Brain } from "lucide-react"

interface DailyStats {
  date: string
  average_stress_level: number | null
  max_stress_level: number | null
  rest_stress_duration: number | null
}

export default function StressPage() {
  const [data, setData] = useState<DailyStats[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/v1/daily-stats?limit=30', {
          headers: {
            'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || '',
          },
        })
        const result = await response.json()
        setData(result.items.reverse())
      } catch (error) {
        console.error('Error fetching stress data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return '--'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const latestData = data.length > 0 ? data[data.length - 1] : null
  const avgStress = data.length > 0 
    ? Math.round(data.reduce((acc, item) => acc + (item.average_stress_level || 0), 0) / data.filter(item => item.average_stress_level).length)
    : 0
  const avgRestTime = data.length > 0 
    ? Math.round(data.reduce((acc, item) => acc + (item.rest_stress_duration || 0), 0) / data.filter(item => item.rest_stress_duration).length)
    : 0

  const chartData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    average: item.average_stress_level || 0,
    max: item.max_stress_level || 0,
  }))

  const getStressLevel = (stress: number | null) => {
    if (!stress) return 'Unknown'
    if (stress < 25) return 'Low'
    if (stress < 50) return 'Medium'
    if (stress < 75) return 'High'
    return 'Very High'
  }

  if (loading) {
    return (
      <PageLayout 
        title="Stress" 
        breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Stress" }]}
      >
        <div className="grid auto-rows-min gap-4 md:grid-cols-3">
          <div className="bg-muted/50 aspect-video rounded-xl animate-pulse" />
          <div className="bg-muted/50 aspect-video rounded-xl animate-pulse" />
          <div className="bg-muted/50 aspect-video rounded-xl animate-pulse" />
        </div>
        <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 animate-pulse" />
      </PageLayout>
    )
  }

  return (
    <PageLayout 
      title="Stress" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Stress" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Latest Stress Level</CardDescription>
            <CardTitle className="text-4xl">{latestData?.average_stress_level || '--'}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground flex items-center gap-1">
              <Brain className="h-4 w-4" />
              {latestData?.average_stress_level ? getStressLevel(latestData?.average_stress_level) : '--'}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Average Stress</CardDescription>
            <CardTitle className="text-4xl">{avgStress}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">
              30-day average - {getStressLevel(avgStress)}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Average Rest Time</CardDescription>
            <CardTitle className="text-4xl">{formatDuration(avgRestTime)}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">
              Daily rest duration
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Stress Level History</CardTitle>
          <CardDescription>Daily stress levels over the last 30 days</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              average: {
                label: "Average Stress",
                color: "var(--chart-1)",
              },
              max: {
                label: "Max Stress",
                color: "var(--chart-2)",
              },
            }}
          >
            <AreaChart
              data={chartData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="colorAvgStress" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--chart-1)" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="var(--chart-1)" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="colorMaxStress" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--chart-2)" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="var(--chart-2)" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis
                dataKey="date"
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                className="text-xs"
              />
              <YAxis
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                domain={[0, 100]}
                className="text-xs"
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Area
                type="monotone"
                dataKey="max"
                stroke="var(--chart-2)"
                fillOpacity={1}
                fill="url(#colorMaxStress)"
              />
              <Area
                type="monotone"
                dataKey="average"
                stroke="var(--chart-1)"
                fillOpacity={1}
                fill="url(#colorAvgStress)"
              />
            </AreaChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </PageLayout>
  )
}
