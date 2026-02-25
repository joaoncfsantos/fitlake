"use client";

import { PageLayout } from "@/components/page-layout";
import { useWorkouts } from "@/hooks/useWorkouts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { RefreshCw, Dumbbell, Clock, Calendar } from "lucide-react";
import { useState } from "react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useDemoMode } from "@/contexts/demo-mode";

export default function WorkoutsAllPage() {
  const { data: workouts, loading, error, refetch } = useWorkouts(100);
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState<string | null>(null);

  const { isDemo } = useDemoMode();

  const handleSync = async () => {
    setSyncError(null);
    setSyncing(true);
    try {
      const response = await fetch("/api/v1/sync/hevy", {
        method: "POST",
        headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
      });

      if (!response.ok) {
        throw new Error("Failed to sync Hevy data");
      }

      await refetch();
    } catch (err) {
      setSyncError(err instanceof Error ? err.message : "Failed to sync data");
    } finally {
      setSyncing(false);
    }
  };

  const handleLightSync = async () => {
    setSyncError(null);
    setSyncing(true);
    try {
      const response = await fetch("/api/v1/sync/hevy?light=true", {
        method: "POST",
        headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
      });

      if (!response.ok) {
        throw new Error("Failed to light sync Hevy data");
      }

      await refetch();
    } catch (err) {
      setSyncError(
        err instanceof Error ? err.message : "Failed to light sync data",
      );
    } finally {
      setSyncing(false);
    }
  };

  // Calculate summary statistics
  const totalWorkouts = workouts.length;
  const totalDuration = workouts.reduce(
    (sum, workout) => sum + workout.duration_seconds,
    0,
  );
  const totalExercises = workouts.reduce(
    (sum, workout) => sum + workout.exercise_count,
    0,
  );
  const avgWorkoutDuration =
    totalWorkouts > 0 ? totalDuration / totalWorkouts : 0;

  // Helper functions
  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);

    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <PageLayout
        title="Workouts - All Activities"
        breadcrumbs={[
          { label: "Workouts", href: "/workouts/all" },
          { label: "All" },
        ]}
      >
        <div className="grid auto-rows-min gap-4 md:grid-cols-3">
          <Skeleton className="aspect-video rounded-xl" />
          <Skeleton className="aspect-video rounded-xl" />
          <Skeleton className="aspect-video rounded-xl" />
        </div>
        <Skeleton className="min-h-[50vh] mt-4 rounded-xl" />
      </PageLayout>
    );
  }

  if (error) {
    return (
      <PageLayout
        title="Workouts - All Activities"
        breadcrumbs={[
          { label: "Workouts", href: "/workouts/all" },
          { label: "All" },
        ]}
      >
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
          Error loading workouts: {error.message}
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout
      title="Workouts - All Activities"
      breadcrumbs={[
        { label: "Workouts", href: "/workouts/all" },
        { label: "All" },
      ]}
      action={
        !isDemo && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button disabled={syncing} variant="outline" size="sm">
                <RefreshCw className={syncing ? "animate-spin" : ""} />
                {syncing ? "Syncing..." : "Sync"}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Sync Options</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuGroup>
                <DropdownMenuItem onClick={handleLightSync}>
                  Light Sync
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleSync}>
                  Full Sync
                </DropdownMenuItem>
              </DropdownMenuGroup>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      }
    >
      {syncError && (
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg mb-4">
          {syncError}
        </div>
      )}

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
            <div className="text-2xl font-bold">{totalWorkouts}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {totalExercises} exercises completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Total Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatDuration(totalDuration)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Time spent training
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Avg Duration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {totalWorkouts > 0 ? formatDuration(avgWorkoutDuration) : "-"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Per workout session
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Workouts List */}
      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Recent Workouts</CardTitle>
        </CardHeader>
        <CardContent>
          {workouts.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No workouts found
            </div>
          ) : (
            <div className="space-y-3">
              {workouts.map((workout) => (
                <div
                  key={workout.id}
                  className="flex flex-col md:flex-row md:items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{workout.title}</h3>
                    <div className="flex flex-wrap gap-2 mt-1 text-sm text-muted-foreground">
                      <span>{formatDate(workout.start_time)}</span>
                      <span>•</span>
                      <span>{formatTime(workout.start_time)}</span>
                      <span>•</span>
                      <span className="capitalize">{workout.platform}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mt-4 md:mt-0 md:ml-4">
                    <div className="text-center">
                      <div className="text-xs text-muted-foreground">
                        Duration
                      </div>
                      <div className="font-semibold">
                        {formatDuration(workout.duration_seconds)}
                      </div>
                    </div>

                    <div className="text-center">
                      <div className="text-xs text-muted-foreground">
                        Exercises
                      </div>
                      <div className="font-semibold">
                        {workout.exercise_count}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </PageLayout>
  );
}
