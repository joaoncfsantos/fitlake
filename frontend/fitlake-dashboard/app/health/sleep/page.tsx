"use client"

import { useEffect, useState } from "react"
import { PageLayout } from "@/components/page-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Bar, BarChart, CartesianGrid, ReferenceLine, XAxis, YAxis } from "recharts"
import { Moon } from "lucide-react"

interface SleepData {
  date: string
  sleepTimeSeconds: number | null
  deepSleepSeconds: number | null
  lightSleepSeconds: number | null
  remSleepSeconds: number | null
  awakeSleepSeconds: number | null
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload
    const formatTime = (seconds: number) => {
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      return `${hours}h ${minutes}m`
    }
    
    const totalSeconds = (data.deepSeconds || 0) + (data.lightSeconds || 0) + (data.remSeconds || 0)
    
    return (
      <div className="rounded-lg border bg-background p-2 shadow-sm">
        <div className="flex flex-col gap-1">
          <span className="text-[0.70rem] uppercase text-muted-foreground">
            {label}
          </span>
          <div className="flex items-center gap-2">
            <div 
              className="h-2.5 w-2.5 shrink-0 rounded-[2px]" 
              style={{ backgroundColor: 'var(--chart-3)' }}
            />
            <span className="text-xs font-medium text-muted-foreground">Deep</span>
            <span className="ml-auto font-bold">
              {formatTime(data.deepSeconds || 0)}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div 
              className="h-2.5 w-2.5 shrink-0 rounded-[2px]" 
              style={{ backgroundColor: 'var(--chart-2)' }}
            />
            <span className="text-xs font-medium text-muted-foreground">Light</span>
            <span className="ml-auto font-bold">
              {formatTime(data.lightSeconds || 0)}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <div 
              className="h-2.5 w-2.5 shrink-0 rounded-[2px]" 
              style={{ backgroundColor: 'var(--chart-1)' }}
            />
            <span className="text-xs font-medium text-muted-foreground">REM</span>
            <span className="ml-auto font-bold">
              {formatTime(data.remSeconds || 0)}
            </span>
          </div>
          <div className="flex items-center gap-2 pt-1 border-t mt-1">
            <span className="text-xs font-medium text-muted-foreground">Total</span>
            <span className="ml-auto font-bold">
              {formatTime(totalSeconds)}
            </span>
          </div>
        </div>
      </div>
    )
  }
  return null
}

export default function SleepPage() {
  const [data, setData] = useState<SleepData[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('/api/v1/sleep?limit=30', {
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

  const formatDecimalHours = (decimalHours: number) => {
    const hours = Math.floor(decimalHours)
    const minutes = Math.round((decimalHours - hours) * 60)
    return `${hours}h${minutes}`
  }

  const latestSleep = data.length > 0 ? data[data.length - 1].sleepTimeSeconds : null
  const avgSleep = data.length > 0 
    ? Math.round(data.reduce((acc, item) => acc + (item.sleepTimeSeconds || 0), 0) / data.filter(item => item.sleepTimeSeconds).length)
    : 0

  const targetSleep = 8 * 3600 // 8 hours in seconds

  const chartData = data.map(item => {
    const deep = item.deepSleepSeconds ? item.deepSleepSeconds / 3600 : null
    const light = item.lightSleepSeconds ? item.lightSleepSeconds / 3600 : null
    const rem = item.remSleepSeconds ? item.remSleepSeconds / 3600 : null
    
    return {
      date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
      deep: deep !== null ? parseFloat(deep.toFixed(1)) : null,
      light: light !== null ? parseFloat(light.toFixed(1)) : null,
      rem: rem !== null ? parseFloat(rem.toFixed(1)) : null,
      deepSeconds: item.deepSleepSeconds || 0,
      lightSeconds: item.lightSleepSeconds || 0,
      remSeconds: item.remSleepSeconds || 0,
    }
  })

  const daysWithData = data.filter(item => item.sleepTimeSeconds !== null).length
  const dataQuality = data.length > 0 ? Math.round((daysWithData / data.length) * 100) : 0

  // Calculate max sleep value and round up to next whole hour
  const validSleepValues = chartData.map(d => {
    const total = (d.deep || 0) + (d.light || 0) + (d.rem || 0)
    return total > 0 ? total : null
  }).filter((v): v is number => v !== null)
  const maxSleepValue = validSleepValues.length > 0 
    ? Math.max(...validSleepValues)
    : 12
  const yAxisMax = Math.ceil(maxSleepValue)

  // Calculate average in hours for the reference line
  const avgSleepHours = avgSleep / 3600

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
          <CardDescription>
            Daily sleep hours over the last 30 days
            {data.length > 0 && ` • ${daysWithData}/${data.length} days with data (${dataQuality}%)`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              deep: {
                label: "Deep Sleep",
                color: "var(--chart-3)",
              },
              light: {
                label: "Light Sleep",
                color: "var(--chart-2)",
              },
              rem: {
                label: "REM Sleep",
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
                domain={[0, yAxisMax]}
                className="text-xs"
              />
              <ChartTooltip content={<CustomTooltip />} />
              <ReferenceLine 
                y={avgSleepHours} 
                stroke="hsl(var(--muted-foreground))" 
                strokeDasharray="3 3"
                label={{ 
                  value: `Avg: ${formatDecimalHours(avgSleepHours)}`, 
                  position: 'left',
                  fill: 'hsl(var(--muted-foreground))',
                  fontSize: 12
                }}
              />
              <Bar
                dataKey="deep"
                stackId="sleep"
                fill="var(--chart-3)"
                radius={[0, 0, 0, 0]}
              />
              <Bar
                dataKey="light"
                stackId="sleep"
                fill="var(--chart-2)"
                radius={[0, 0, 0, 0]}
              />
              <Bar
                dataKey="rem"
                stackId="sleep"
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
