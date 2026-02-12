"use client"

import { useEffect, useState } from "react"
import { PageLayout } from "@/components/page-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { Moon } from "lucide-react"

interface DailyStats {
  date: string
  sleeping_seconds: number | null
}

export default function SleepPage() {
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
        console.error('Error fetching sleep data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const formatHours = (seconds: number | null) => {
    if (!seconds) return '--'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const latestSleep = data.length > 0 ? data[data.length - 1].sleeping_seconds : null
  const avgSleep = data.length > 0 
    ? Math.round(data.reduce((acc, item) => acc + (item.sleeping_seconds || 0), 0) / data.filter(item => item.sleeping_seconds).length)
    : 0

  const targetSleep = 8 * 3600 // 8 hours in seconds

  const chartData = data.map(item => {
    const hours = item.sleeping_seconds ? item.sleeping_seconds / 3600 : 0
    return {
      date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      sleep: parseFloat(hours.toFixed(1)),
    }
  })

  if (loading) {
    return (
      <PageLayout 
        title="Sleep" 
        breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Sleep" }]}
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
      title="Sleep" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Sleep" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Last Night</CardDescription>
            <CardTitle className="text-4xl">{formatHours(latestSleep)}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground flex items-center gap-1">
              <Moon className="h-4 w-4" />
              Total sleep time
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Average Sleep</CardDescription>
            <CardTitle className="text-4xl">{formatHours(avgSleep)}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">
              30-day average
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Sleep Goal</CardDescription>
            <CardTitle className="text-4xl">8h</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-xs text-muted-foreground">
              {avgSleep >= targetSleep ? '✓ Meeting goal' : `${formatHours(targetSleep - avgSleep)} short`}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Sleep Duration</CardTitle>
          <CardDescription>Daily sleep hours over the last 30 days</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              sleep: {
                label: "Sleep (hours)",
                color: "var(--chart-1)",
              },
            }}
          >
            <BarChart
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
                domain={[0, 12]}
                className="text-xs"
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Bar
                dataKey="sleep"
                fill="var(--chart-1)"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </PageLayout>
  )
}
