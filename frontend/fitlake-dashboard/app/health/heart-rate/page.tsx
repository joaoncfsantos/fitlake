"use client"

import { useEffect, useState } from "react"
import { PageLayout } from "@/components/page-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendContent } from "@/components/ui/chart"
import { Line, LineChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { Activity } from "lucide-react"

interface DailyStats {
  date: string
  resting_heart_rate: number | null
  max_heart_rate: number | null
  min_heart_rate: number | null
}

export default function HeartRatePage() {
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
        console.error('Error fetching heart rate data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const latestData = data.length > 0 ? data[data.length - 1] : null
  const avgRestingHR = data.length > 0 
    ? Math.round(data.reduce((acc, item) => acc + (item.resting_heart_rate || 0), 0) / data.filter(item => item.resting_heart_rate).length)
    : 0
  const avgMaxHR = data.length > 0 
    ? Math.round(data.reduce((acc, item) => acc + (item.max_heart_rate || 0), 0) / data.filter(item => item.max_heart_rate).length)
    : 0

  const chartData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    resting: item.resting_heart_rate || null,
    max: item.max_heart_rate || null,
    min: item.min_heart_rate || null,
  }))

  if (loading) {
    return (
      <PageLayout 
        title="Heart Rate" 
        breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Heart Rate" }]}
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
      title="Heart Rate" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Heart Rate" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Resting HR (Latest)</CardDescription>
            <CardTitle className="text-4xl">{latestData?.resting_heart_rate || '--'}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground flex items-center gap-1">
              <Activity className="h-4 w-4" />
              bpm
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Average Resting HR</CardDescription>
            <CardTitle className="text-4xl">{avgRestingHR}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">
              30-day average
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Average Max HR</CardDescription>
            <CardTitle className="text-4xl">{avgMaxHR}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">
              30-day average
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Heart Rate History</CardTitle>
          <CardDescription>Daily heart rate trends over the last 30 days</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              resting: {
                label: "Resting HR",
                color: "var(--chart-1)",
              },
              max: {
                label: "Max HR",
                color: "var(--chart-2)",
              },
              min: {
                label: "Min HR",
                color: "var(--chart-3)",
              },
            }}
            className="h-[40vh] w-full"
          >
            <LineChart
              data={chartData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
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
                domain={[30, 200]}
                className="text-xs"
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <ChartLegend content={<ChartLegendContent payload={[]} />} />
              <Line
                type="monotone"
                dataKey="max"
                stroke="var(--chart-2)"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="resting"
                stroke="var(--chart-1)"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="min"
                stroke="var(--chart-3)"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </PageLayout>
  )
}
