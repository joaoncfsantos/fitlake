"use client"

import { PageLayout } from "@/components/page-layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Area, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts"
import { useDailyStats } from "@/hooks/useDailyStats"

interface DailyStats {
  date: string
  body_battery_highest_value: number | null
  body_battery_lowest_value: number | null
  body_battery_charged_value: number | null
  body_battery_drained_value: number | null
}

export default function BodyBatteryPage() {
  const { data, loading, error } = useDailyStats(30)

  const chartData = data.map((item: DailyStats) => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    highest: item.body_battery_highest_value,
    lowest: item.body_battery_lowest_value,
    charged: item.body_battery_charged_value,
    drained: item.body_battery_drained_value,
  }))

  const daysWithData = data.filter((item: DailyStats) => 
    item.body_battery_highest_value !== null || 
    item.body_battery_lowest_value !== null
  ).length
  const dataQuality = data.length > 0 ? Math.round((daysWithData / data.length) * 100) : 0

  const validMorningData = data.filter((item: DailyStats) => item.body_battery_highest_value !== null)
  const avgMorningBattery = validMorningData.length > 0 
    ? Math.round(validMorningData.reduce((acc: number, item: DailyStats) => acc + (item.body_battery_highest_value || 0), 0) / validMorningData.length)
    : 0

  const validDrainData = data.filter((item: DailyStats) => item.body_battery_drained_value !== null)
  const avgDailyDrain = validDrainData.length > 0 
    ? Math.round(validDrainData.reduce((acc: number, item: DailyStats) => acc + (item.body_battery_drained_value || 0), 0) / validDrainData.length)
    : 0

  const validChargedData = data.filter((item: DailyStats) => item.body_battery_charged_value !== null)
  const avgCharged = validChargedData.length > 0 
    ? Math.round(validChargedData.reduce((acc: number, item: DailyStats) => acc + (item.body_battery_charged_value || 0), 0) / validChargedData.length)
    : 0

  if (loading) {
    return (
      <PageLayout 
        title="Body Battery" 
        breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Body Battery" }]}
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
      title="Body Battery" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Body Battery" }]}
    >
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="flex flex-col">
          <CardHeader className="pb-3">
            <CardTitle>Average Morning Battery</CardTitle>
            <CardDescription>30-day average starting energy</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex items-center justify-center pb-4">
            <div className="text-center">
              <div className="text-5xl font-bold text-foreground">{avgMorningBattery}</div>
              <div className="text-sm text-muted-foreground mt-2">points</div>
            </div>
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader className="pb-3">
            <CardTitle>Average Daily Drain</CardTitle>
            <CardDescription>30-day average energy expenditure</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex items-center justify-center pb-4">
            <div className="text-center">
              <div className="text-5xl font-bold text-foreground">{avgDailyDrain}</div>
              <div className="text-sm text-muted-foreground mt-2">points per day</div>
            </div>
          </CardContent>
        </Card>

        <Card className="flex flex-col">
          <CardHeader className="pb-3">
            <CardTitle>Average Charge</CardTitle>
            <CardDescription>30-day average charged per day</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex items-center justify-center pb-4">
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
          <CardDescription>
            Daily highest and lowest values over the last 30 days
            {data.length > 0 && ` • ${daysWithData}/${data.length} days with data (${dataQuality}%)`}
          </CardDescription>
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
            className="h-[40vh] w-full"
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
                connectNulls={false}
              />
              <Area
                type="monotone"
                dataKey="lowest"
                stroke="var(--chart-2)"
                fillOpacity={1}
                fill="url(#colorLowest)"
                connectNulls={false}
              />
            </AreaChart>
          </ChartContainer>
        </CardContent>
      </Card>
    </PageLayout>
  )
}
