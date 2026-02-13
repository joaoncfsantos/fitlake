"use client"

import { useEffect, useState } from "react"
import { PageLayout } from "@/components/page-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, RadialBarChart, RadialBar, PolarGrid, PolarRadiusAxis, ReferenceLine } from "recharts"
import { Footprints } from "lucide-react"

interface DailyStats {
  date: string
  steps: number | null
  daily_step_goal: number | null
}

export default function StepsPage() {
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
        console.error('Error fetching steps data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const latestData = data.length > 0 ? data[data.length - 1] : null
  const todaySteps = latestData?.steps || 0
  const stepGoal = latestData?.daily_step_goal || 10000
  const goalProgress = Math.round((todaySteps / stepGoal) * 100)

  const avgSteps = data.length > 0 
    ? Math.round(data.reduce((acc, item) => acc + (item.steps || 0), 0) / data.filter(item => item.steps).length)
    : 0

  const chartData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    steps: item.steps || 0,
    goal: item.daily_step_goal || 10000,
  }))

  const radialData = [{ value: goalProgress, fill: 'var(--chart-1)' }]

  if (loading) {
    return (
      <PageLayout 
        title="Steps" 
        breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Steps" }]}
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
      title="Steps" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Steps" }]}
    >
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="flex flex-col">
          <CardHeader className="pb-2">
            <CardDescription>Today's Steps</CardDescription>
            <CardTitle className="text-4xl">{todaySteps.toLocaleString()}</CardTitle>
          </CardHeader>
          <CardContent className="pb-4">
            <div className="text-xs text-muted-foreground flex items-center gap-1">
              <Footprints className="h-4 w-4" />
              Latest recorded
            </div>
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader className="pb-2">
            <CardDescription>Daily Average</CardDescription>
            <CardTitle className="text-4xl">{avgSteps.toLocaleString()}</CardTitle>
          </CardHeader>
            <CardContent className="pb-4">
            <div className="text-xs text-muted-foreground">
              30-day average
            </div>
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader className="pb-3">
            <CardTitle>Goal Progress</CardTitle>
            <CardDescription>{stepGoal.toLocaleString()} steps goal</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex items-center justify-center pb-4">
            <ChartContainer
              config={{
                progress: {
                  label: "Progress",
                  color: "var(--chart-1)",
                },
              }}
              className="aspect-square max-h-[180px] w-full"
            >
              <RadialBarChart
                data={radialData}
                startAngle={90}
                endAngle={90 - (Math.min(goalProgress, 100) / 100) * 360}
                innerRadius={60}
                outerRadius={80}
              >
                <PolarGrid
                  gridType="circle"
                  radialLines={false}
                  stroke="none"
                  className="first:fill-muted last:fill-background"
                  polarRadius={[66, 54]}
                />
                <RadialBar dataKey="value" background cornerRadius={10} />
                <PolarRadiusAxis tick={false} tickLine={false} axisLine={false}>
                  <text
                    x="50%"
                    y="50%"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="fill-foreground text-3xl font-bold"
                  >
                    {goalProgress}%
                  </text>
                </PolarRadiusAxis>
              </RadialBarChart>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Steps History</CardTitle>
          <CardDescription>Daily steps over the last 30 days with goal reference line</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              steps: {
                label: "Steps",
                color: "var(--chart-1)",
              },
            }}
            className="h-[40vh] w-full"
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
                className="text-xs"
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <ReferenceLine 
                y={stepGoal} 
                stroke="var(--chart-2)" 
                strokeDasharray="3 3"
                label={{ value: 'Goal', position: 'right', fill: 'var(--muted-foreground)' }}
              />
              <Bar
                dataKey="steps"
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
