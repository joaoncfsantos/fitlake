"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { PageLayout } from "@/components/page-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Area, AreaChart, Line, LineChart, Bar, BarChart } from "recharts"
import { Battery, Heart, Moon, Footprints, Brain, Zap, ArrowRight, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"

interface DailyStats {
  date: string
  body_battery_highest_value: number | null
  resting_heart_rate: number | null
  sleeping_seconds: number | null
  steps: number | null
  average_stress_level: number | null
}

export default function HealthAllPage() {
  const [data, setData] = useState<DailyStats[]>([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)

  const fetchData = async () => {
    try {
      const response = await fetch('/api/v1/daily-stats?limit=14', {
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || '',
        },
      })
      const result = await response.json()
      setData(result.items.reverse())
    } catch (error) {
      console.error('Error fetching health data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSync = async () => {
    setSyncing(true)
    try {
      // Sync from Garmin to database
      const syncResponse = await fetch('/api/v1/sync/garmin', {
        method: 'POST',
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || '',
        },
      })
      
      if (!syncResponse.ok) {
        throw new Error('Sync failed')
      }
      
      // Fetch the updated data from database
      await fetchData()
    } catch (error) {
      console.error('Error syncing Garmin data:', error)
    } finally {
      setSyncing(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const calculateReadinessScore = (item: DailyStats): number => {
    let score = 0
    let factors = 0
    if (item.body_battery_highest_value) { score += item.body_battery_highest_value * 0.4; factors++ }
    if (item.sleeping_seconds) { score += Math.min((item.sleeping_seconds / 3600 / 8) * 100, 100) * 0.3; factors++ }
    if (item.average_stress_level !== null) { score += (100 - item.average_stress_level) * 0.2; factors++ }
    if (item.resting_heart_rate) { score += Math.max(0, 100 - Math.abs(item.resting_heart_rate - 60)) * 0.1; factors++ }
    return factors > 0 ? Math.round(score) : 0
  }

  const batteryData = data.map(item => ({ value: item.body_battery_highest_value || 0 }))
  const heartRateData = data.map(item => ({ value: item.resting_heart_rate || 0 }))
  const sleepData = data.map(item => ({ value: item.sleeping_seconds ? item.sleeping_seconds / 3600 : 0 }))
  const stepsData = data.map(item => ({ value: item.steps || 0 }))
  const stressData = data.map(item => ({ value: item.average_stress_level || 0 }))
  const readinessData = data.map(item => ({ value: calculateReadinessScore(item) }))

  const latestData = data.length > 0 ? data[data.length - 1] : null

  if (loading) {
    return (
      <PageLayout 
        title="Health - All Metrics" 
        breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "All" }]}
        action={
          <Button 
            onClick={handleSync}
            disabled={syncing}
            variant="outline"
            size="sm"
          >
            <RefreshCw className={syncing ? "animate-spin" : ""} />
            {syncing ? "Syncing..." : "Sync"}
          </Button>
        }
      >
        <div className="grid auto-rows-min gap-4 md:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-muted/50 aspect-video rounded-xl animate-pulse" />
          ))}
        </div>
      </PageLayout>
    )
  }

  const MetricCard = ({ 
    title, 
    value, 
    unit, 
    icon: Icon, 
    data, 
    chartType = 'area',
    href 
  }: { 
    title: string
    value: string | number
    unit: string
    icon: any
    data: any[]
    chartType?: 'area' | 'line' | 'bar'
    href: string
  }) => (
    <Link href={href}>
      <Card className="cursor-pointer hover:bg-accent/50 transition-colors">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardDescription className="flex items-center gap-2">
              <Icon className="h-4 w-4" />
              {title}
            </CardDescription>
            <ArrowRight className="h-4 w-4 text-muted-foreground" />
          </div>
          <CardTitle className="text-2xl">{value} <span className="text-sm font-normal text-muted-foreground">{unit}</span></CardTitle>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              value: {
                label: title,
                color: "var(--chart-1)",
              },
            }}
            className="h-[80px] w-full"
          >
            {chartType === 'area' && (
              <AreaChart data={data}>
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="var(--chart-1)"
                  fill="var(--chart-1)"
                  fillOpacity={0.2}
                  strokeWidth={2}
                />
              </AreaChart>
            )}
            {chartType === 'line' && (
              <LineChart data={data}>
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="var(--chart-1)"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            )}
            {chartType === 'bar' && (
              <BarChart data={data}>
                <Bar
                  dataKey="value"
                  fill="var(--chart-1)"
                  radius={[2, 2, 0, 0]}
                />
              </BarChart>
            )}
          </ChartContainer>
        </CardContent>
      </Card>
    </Link>
  )

  return (
    <PageLayout 
      title="Health - All Metrics" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "All" }]}
      action={
        <Button 
          onClick={handleSync}
          disabled={syncing}
          variant="outline"
          size="sm"
        >
          <RefreshCw className={syncing ? "animate-spin" : ""} />
          {syncing ? "Syncing..." : "Sync"}
        </Button>
      }
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <MetricCard
          title="Body Battery"
          value={latestData?.body_battery_highest_value || '--'}
          unit=""
          icon={Battery}
          data={batteryData}
          chartType="area"
          href="/health/body-battery"
        />
        <MetricCard
          title="Heart Rate"
          value={latestData?.resting_heart_rate || '--'}
          unit="bpm"
          icon={Heart}
          data={heartRateData}
          chartType="line"
          href="/health/heart-rate"
        />
        <MetricCard
          title="Sleep"
          value={latestData?.sleeping_seconds ? `${(latestData.sleeping_seconds / 3600).toFixed(1)}` : '--'}
          unit="hours"
          icon={Moon}
          data={sleepData}
          chartType="bar"
          href="/health/sleep"
        />
      </div>
      
      <div className="grid auto-rows-min gap-4 md:grid-cols-3 mt-4">
        <MetricCard
          title="Steps"
          value={latestData?.steps?.toLocaleString() || '--'}
          unit=""
          icon={Footprints}
          data={stepsData}
          chartType="bar"
          href="/health/steps"
        />
        <MetricCard
          title="Stress"
          value={latestData?.average_stress_level || '--'}
          unit=""
          icon={Brain}
          data={stressData}
          chartType="area"
          href="/health/stress"
        />
        <MetricCard
          title="Training Readiness"
          value={latestData ? calculateReadinessScore(latestData) : '--'}
          unit=""
          icon={Zap}
          data={readinessData}
          chartType="line"
          href="/health/training-readiness"
        />
      </div>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Health Overview</CardTitle>
          <CardDescription>14-day snapshot of all health metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Recovery Metrics</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li className="flex items-center gap-2">
                    <Battery className="h-3 w-3" />
                    Body Battery tracking energy levels throughout the day
                  </li>
                  <li className="flex items-center gap-2">
                    <Moon className="h-3 w-3" />
                    Sleep duration monitoring for optimal recovery
                  </li>
                  <li className="flex items-center gap-2">
                    <Brain className="h-3 w-3" />
                    Stress levels indicating mental and physical strain
                  </li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Activity Metrics</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li className="flex items-center gap-2">
                    <Heart className="h-3 w-3" />
                    Resting heart rate as a recovery indicator
                  </li>
                  <li className="flex items-center gap-2">
                    <Footprints className="h-3 w-3" />
                    Daily steps for general activity tracking
                  </li>
                  <li className="flex items-center gap-2">
                    <Zap className="h-3 w-3" />
                    Training readiness composite score
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </PageLayout>
  )
}
