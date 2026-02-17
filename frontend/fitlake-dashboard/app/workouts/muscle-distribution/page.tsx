"use client";

import { PageLayout } from "@/components/page-layout";
import { useMuscleDistribution } from "@/hooks/useMuscleDistribution";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Pie, PieChart, Cell, Legend } from "recharts";
import { Dumbbell, Target, TrendingUp } from "lucide-react";

// Color palette for muscle groups
const COLORS = [
  "hsl(var(--chart-1))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
  "hsl(var(--chart-5))",
  "#8b5cf6",
  "#ec4899",
  "#f59e0b",
  "#10b981",
  "#06b6d4",
  "#6366f1",
  "#f43f5e",
];

export default function MuscleDistributionPage() {
  const { data, loading, error } = useMuscleDistribution();

  if (loading) {
    return (
      <PageLayout
        title="Muscle Distribution"
        breadcrumbs={[
          { label: "Workouts", href: "/workouts/all" },
          { label: "Muscle Distribution" },
        ]}
      >
        <div className="grid auto-rows-min gap-4 md:grid-cols-3">
          <Skeleton className="aspect-video rounded-xl" />
          <Skeleton className="aspect-video rounded-xl" />
          <Skeleton className="aspect-video rounded-xl" />
        </div>
        <div className="grid gap-4 md:grid-cols-2 mt-4">
          <Skeleton className="aspect-video rounded-xl" />
          <Skeleton className="aspect-video rounded-xl" />
        </div>
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout
        title="Muscle Distribution"
        breadcrumbs={[
          { label: "Workouts", href: "/workouts/all" },
          { label: "Muscle Distribution" },
        ]}
      >
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
          Error loading muscle distribution: {error.message}
        </div>
      </PageLayout>
    );
  }

  if (!data || data.muscle_distribution.length === 0) {
    return (
      <PageLayout
        title="Muscle Distribution"
        breadcrumbs={[
          { label: "Workouts", href: "/workouts/all" },
          { label: "Muscle Distribution" },
        ]}
      >
        <div className="text-center py-12 text-muted-foreground">
          No muscle distribution data available. Complete some workouts first.
        </div>
      </PageLayout>
    );
  }

  // Prepare data for charts
  const barChartData = data.muscle_distribution.map((item) => ({
    name: item.muscle_group,
    weightedSets: item.weighted_sets,
    totalSets: item.total_sets,
  }));

  const pieChartData = data.muscle_distribution.map((item) => ({
    name: item.muscle_group,
    value: item.weighted_sets,
    percentage: item.percentage,
  }));

  // Get top muscle group
  const topMuscle = data.muscle_distribution[0];

  // Chart config
  const chartConfig = {
    weightedSets: {
      label: "Weighted Sets",
      color: "hsl(var(--chart-1))",
    },
  };

  return (
    <PageLayout
      title="Muscle Distribution"
      breadcrumbs={[
        { label: "Workouts", href: "/workouts/all" },
        { label: "Muscle Distribution" },
      ]}
    >
      {/* Summary Cards */}
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Dumbbell className="h-4 w-4" />
              Total Workouts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.total_workouts}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {data.total_sets} total sets
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Target className="h-4 w-4" />
              Top Muscle Group
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold capitalize">
              {topMuscle.muscle_group}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {topMuscle.percentage.toFixed(1)}% of training
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Training Balance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.muscle_distribution.length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Muscle groups trained
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2 mt-4">
        {/* Bar Chart - Weighted Sets per Muscle Group */}
        <Card>
          <CardHeader>
            <CardTitle>Muscle Group Volume</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig}>
              <BarChart data={barChartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis
                  dataKey="name"
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  className="text-xs"
                  tick={{ fill: "hsl(var(--muted-foreground))" }}
                />
                <YAxis
                  className="text-xs"
                  tick={{ fill: "hsl(var(--muted-foreground))" }}
                  label={{
                    value: "Weighted Sets",
                    angle: -90,
                    position: "insideLeft",
                    style: { fill: "hsl(var(--muted-foreground))" },
                  }}
                />
                <ChartTooltip
                  content={({ active, payload }) => {
                    if (!active || !payload || payload.length === 0) return null;
                    const data = payload[0].payload;
                    return (
                      <div className="rounded-lg border bg-background p-2 shadow-sm">
                        <div className="flex flex-col gap-1">
                          <span className="text-sm font-semibold capitalize">
                            {data.name}
                          </span>
                          <div className="text-xs text-muted-foreground">
                            Weighted Sets: {data.weightedSets.toFixed(1)}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Total Sets: {data.totalSets}
                          </div>
                        </div>
                      </div>
                    );
                  }}
                />
                <Bar
                  dataKey="weightedSets"
                  fill="hsl(var(--chart-1))"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Pie Chart - Percentage Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Training Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ChartContainer config={chartConfig} className="mx-auto">
              <PieChart>
                <Pie
                  data={pieChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry: any) =>
                    entry.percentage > 5 ? `${entry.name} ${entry.percentage.toFixed(0)}%` : ""
                  }
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieChartData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <ChartTooltip
                  content={({ active, payload }) => {
                    if (!active || !payload || payload.length === 0) return null;
                    const data = payload[0].payload;
                    return (
                      <div className="rounded-lg border bg-background p-2 shadow-sm">
                        <div className="flex flex-col gap-1">
                          <span className="text-sm font-semibold capitalize">
                            {data.name}
                          </span>
                          <div className="text-xs text-muted-foreground">
                            {data.percentage.toFixed(1)}% of training
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {data.value.toFixed(1)} weighted sets
                          </div>
                        </div>
                      </div>
                    );
                  }}
                />
              </PieChart>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Table */}
      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Detailed Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2 px-4 font-medium">
                    Muscle Group
                  </th>
                  <th className="text-right py-2 px-4 font-medium">
                    Weighted Sets
                  </th>
                  <th className="text-right py-2 px-4 font-medium">
                    Total Sets
                  </th>
                  <th className="text-right py-2 px-4 font-medium">
                    Percentage
                  </th>
                </tr>
              </thead>
              <tbody>
                {data.muscle_distribution.map((item, index) => (
                  <tr key={index} className="border-b hover:bg-muted/50">
                    <td className="py-2 px-4 capitalize">{item.muscle_group}</td>
                    <td className="text-right py-2 px-4">
                      {item.weighted_sets.toFixed(1)}
                    </td>
                    <td className="text-right py-2 px-4">{item.total_sets}</td>
                    <td className="text-right py-2 px-4">
                      {item.percentage.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Explanation */}
      <Card className="mt-4">
        <CardHeader>
          <CardTitle className="text-sm">How is this calculated?</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          <p>
            Muscle distribution is calculated using weighted sets. Primary muscle
            groups receive a weight of {data.primary_muscle_weight.toFixed(1)},
            while secondary muscle groups receive a weight of{" "}
            {data.secondary_muscle_weight.toFixed(1)}. This provides a more
            accurate representation of which muscles are being trained most
            heavily.
          </p>
        </CardContent>
      </Card>
    </PageLayout>
  );
}
