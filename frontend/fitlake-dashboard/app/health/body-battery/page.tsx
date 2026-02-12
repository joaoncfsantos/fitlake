"use client"

import { useEffect, useState } from "react"
import { PageLayout } from "@/components/page-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Area, AreaChart, CartesianGrid, XAxis, YAxis, RadialBarChart, RadialBar, PolarGrid, PolarRadiusAxis } from "recharts"

interface DailyStats {
  date: string
  body_battery_highest_value: number | null
  body_battery_lowest_value: number | null
  body_battery_charged_value: number | null
  body_battery_drained_value: number | null
}

export default function BodyBatteryPage() {
  const [data, setData] = useState<DailyStats[]>([])
  const [loading, setLoading] = useState(true)
  //TODO: Get actual current battery 
  const [currentBattery, setCurrentBattery] = useState(0)

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
        
        // For now, set current battery to most recent highest value
        if (result.items.length > 0) {
          setCurrentBattery(result.items[0].body_battery_highest_value || 0)
        }
      } catch (error) {
        console.error('Error fetching body battery data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const chartData = data.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    highest: item.body_battery_highest_value || 0,
    lowest: item.body_battery_lowest_value || 0,
    charged: item.body_battery_charged_value || 0,
    drained: item.body_battery_drained_value || 0,
  }))

  const radialData = [{ name: 'battery', value: currentBattery, fill: 'var(--chart-1)' }]

  const avgCharged = data.length > 0 
    ? Math.round(data.reduce((acc, item) => acc + (item.body_battery_charged_value || 0), 0) / data.length)
    : 0

  if (loading) {
    return (
      <PageLayout 
        title="Body Battery" 
        breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Body Battery" }]}
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
      title="Body Battery" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Body Battery" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Current Body Battery</CardTitle>
            <CardDescription>Latest recorded value</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer
              config={{
                battery: {
                  label: "Battery",
                  color: "var(--chart-1)",
                },
              }}
              className="mx-auto aspect-square max-h-[250px]"
            >
              <RadialBarChart
                data={radialData}
                startAngle={90}
                endAngle={90 - (currentBattery / 100) * 360}
                innerRadius={80}
                outerRadius={110}
              >
                <PolarGrid
                  gridType="circle"
                  radialLines={false}
                  stroke="none"
                  className="first:fill-muted last:fill-background"
                  polarRadius={[86, 74]}
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
                    {currentBattery}
                  </text>
                </PolarRadiusAxis>
              </RadialBarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Average Charge</CardTitle>
            <CardDescription>30-day average charged per day</CardDescription>
          </CardHeader>
          <CardContent className="flex items-center justify-center min-h-[250px]">
            <div className="text-center">
              <div className="text-5xl font-bold text-foreground">{avgCharged}</div>
              <div className="text-sm text-muted-foreground mt-2">points per day</div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Body Battery History</CardTitle>
          <CardDescription>Daily highest and lowest values over the last 30 days</CardDescription>
        </CardHeader>
        <CardContent>
          <ChartContainer
            config={{
              highest: {
                label: "Highest",
                color: "var(--chart-1)",
              },
              lowest: {
                label: "Lowest",
                color: "var(--chart-2)",
              },
            }}
          >
            <AreaChart
              data={chartData}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <defs>
                <linearGradient id="colorHighest" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--chart-1)" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="var(--chart-1)" stopOpacity={0.1}/>
                </linearGradient>
                <linearGradient id="colorLowest" x1="0" y1="0" x2="0" y2="1">
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
                dataKey="highest"
                stroke="var(--chart-1)"
                fillOpacity={1}
                fill="url(#colorHighest)"
              />
              <Area
                type="monotone"
                dataKey="lowest"
                stroke="var(--chart-2)"
                fillOpacity={1}
                fill="url(#colorLowest)"
              />
            </AreaChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </PageLayout>
  )
}
