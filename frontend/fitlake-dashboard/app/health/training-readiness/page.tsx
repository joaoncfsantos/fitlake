"use client"

import { useEffect, useState } from "react"
import { PageLayout } from "@/components/page-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Line, LineChart, CartesianGrid, XAxis, YAxis, RadialBarChart, RadialBar, PolarGrid, PolarRadiusAxis } from "recharts"
import { Zap } from "lucide-react"

interface DailyStats {
  date: string
  body_battery_highest_value: number | null
  sleeping_seconds: number | null
  average_stress_level: number | null
  resting_heart_rate: number | null
}

export default function TrainingReadinessPage() {
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
        console.error('Error fetching training readiness data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  // Calculate training readiness score based on multiple factors
  const calculateReadinessScore = (item: DailyStats): number => {
    let score = 0
    let factors = 0

    // Body Battery (40% weight)
    if (item.body_battery_highest_value) {
      score += item.body_battery_highest_value * 0.4
      factors++
    }

    // Sleep Quality (30% weight) - 8 hours = 100%
    if (item.sleeping_seconds) {
      const sleepHours = item.sleeping_seconds / 3600
      const sleepScore = Math.min((sleepHours / 8) * 100, 100)
      score += sleepScore * 0.3
      factors++
    }

    // Stress Level (20% weight) - inverted, lower is better
    if (item.average_stress_level !== null) {
      score += (100 - item.average_stress_level) * 0.2
      factors++
    }

    // Resting Heart Rate (10% weight) - normalized around 60 bpm
    if (item.resting_heart_rate) {
      const hrScore = Math.max(0, 100 - Math.abs(item.resting_heart_rate - 60))
      score += hrScore * 0.1
      factors++
    }

    return factors > 0 ? Math.round(score) : 0
  }

  const chartData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    readiness: calculateReadinessScore(item),
  }))

  const latestReadiness = chartData.length > 0 ? chartData[chartData.length - 1].readiness : 0
  const avgReadiness = chartData.length > 0 
    ? Math.round(chartData.reduce((acc, item) => acc + item.readiness, 0) / chartData.length)
    : 0

  const radialData = [{ value: latestReadiness, fill: 'var(--chart-1)' }]

  const getRecoveryStatus = (score: number) => {
    if (score >= 80) return { status: 'Excellent', color: 'text-green-600' }
    if (score >= 60) return { status: 'Good', color: 'text-blue-600' }
    if (score >= 40) return { status: 'Fair', color: 'text-yellow-600' }
    return { status: 'Poor', color: 'text-red-600' }
  }

  const recovery = getRecoveryStatus(latestReadiness)

  if (loading) {
    return (
      <PageLayout 
        title="Training Readiness" 
        breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Training Readiness" }]}
      >
        <div className="grid auto-rows-min gap-4 md:grid-cols-2">
          <div className="bg-muted/50 aspect-video rounded-xl animate-pulse" />
          <div className="bg-muted/50 aspect-video rounded-xl animate-pulse" />
        </div>
        <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 animate-pulse" />
      </PageLayout>
    )
  }

  return (
    <PageLayout 
      title="Training Readiness" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Training Readiness" }]}
    >
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="flex flex-col">
          <CardHeader className="pb-3">
            <CardTitle>Readiness Score</CardTitle>
            <CardDescription>Composite score based on sleep, stress, and recovery</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex items-center justify-center pb-4">
            <ChartContainer
              config={{
                readiness: {
                  label: "Readiness",
                  color: "var(--chart-1)",
                },
              }}
              className="aspect-square max-h-[180px] w-full"
            >
              <RadialBarChart
                data={radialData}
                startAngle={90}
                endAngle={90 - (latestReadiness / 100) * 360}
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
                    className="fill-foreground text-4xl font-bold"
                  >
                    {latestReadiness}
                  </text>
                </PolarRadiusAxis>
              </RadialBarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader className="pb-3">
            <CardTitle>Recovery Status</CardTitle>
            <CardDescription>Current training readiness assessment</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col items-center justify-center pb-4">
            <div className="text-center">
              <Zap className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <div className={`text-3xl font-bold ${recovery.color}`}>{recovery.status}</div>
              <div className="text-sm text-muted-foreground mt-2">
                30-day avg: {avgReadiness}
              </div>
              <div className="text-xs text-muted-foreground mt-4">
                {latestReadiness >= 80 && "You're well-recovered and ready for intense training"}
                {latestReadiness >= 60 && latestReadiness < 80 && "Good recovery, suitable for moderate training"}
                {latestReadiness >= 40 && latestReadiness < 60 && "Consider lighter training today"}
                {latestReadiness < 40 && "Focus on recovery and rest"}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Training Readiness Trends</CardTitle>
          <CardDescription>Daily readiness score over the last 30 days</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              readiness: {
                label: "Readiness Score",
                color: "var(--chart-1)",
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
                domain={[0, 100]}
                className="text-xs"
              />
              <ChartTooltip content={<ChartTooltipContent />} />
              <Line
                type="monotone"
                dataKey="readiness"
                stroke="var(--chart-1)"
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
