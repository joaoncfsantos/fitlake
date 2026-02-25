"use client";

import { PageLayout } from "@/components/page-layout";
import { useRunningActivities } from "@/hooks/useRunningActivities";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { ChevronDown, MoreHorizontal, RefreshCw } from "lucide-react";
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

export default function RunningAllPage() {
  const {
    data: activities,
    loading,
    error,
    refetch,
  } = useRunningActivities(100);
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState<string | null>(null);

  const { isDemo } = useDemoMode();

  const handleSync = async () => {
    setSyncError(null);
    setSyncing(true);
    try {
      const response = await fetch("/api/v1/sync/strava", {
        method: "POST",
        headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
      });

      if (!response.ok) {
        throw new Error("Failed to sync Strava data");
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
      const response = await fetch("/api/v1/sync/strava?light=true", {
        method: "POST",
        headers: { "X-API-Key": process.env.NEXT_PUBLIC_API_KEY || "" },
      });

      if (!response.ok) {
        throw new Error("Failed to light sync Strava data");
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
  const totalDistance = activities.reduce(
    (sum, act) => sum + (act.distance_meters || 0),
    0,
  );
  const totalTime = activities.reduce(
    (sum, act) => sum + act.elapsed_time_seconds,
    0,
  );
  const totalActivities = activities.length;

  // Calculate average pace (minutes per km)
  const avgPace =
    totalDistance > 0 ? totalTime / 60 / (totalDistance / 1000) : 0;

  // Helper functions
  const formatDistance = (meters: number) => {
    return (meters / 1000).toFixed(2) + " km";
  };

  const formatPace = (minPerKm: number) => {
    const minutes = Math.floor(minPerKm);
    const seconds = Math.round((minPerKm - minutes) * 60);
    return `${minutes}:${seconds.toString().padStart(2, "0")} /km`;
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    }
    return `${minutes}m ${secs}s`;
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
        title="Running - All Activities"
        breadcrumbs={[
          { label: "Running", href: "/running/all" },
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
        title="Running - All Activities"
        breadcrumbs={[
          { label: "Running", href: "/running/all" },
          { label: "All" },
        ]}
      >
        <div className="bg-destructive/10 text-destructive p-4 rounded-lg">
          Error loading activities: {error.message}
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout
      title="Running - All Activities"
      breadcrumbs={[
        { label: "Running", href: "/running/all" },
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
      {/* Summary Cards */}
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Distance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatDistance(totalDistance)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {totalActivities} {totalActivities === 1 ? "run" : "runs"}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Average Pace
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {totalActivities > 0 ? formatPace(avgPace) : "-"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Across all runs
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatDuration(totalTime)}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Time spent running
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Activities List */}
      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Recent Activities</CardTitle>
        </CardHeader>
        <CardContent>
          {activities.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              No running activities found
            </div>
          ) : (
            <div className="space-y-3">
              {activities.map((activity) => (
                <div
                  key={activity.id}
                  className="flex flex-col md:flex-row md:items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{activity.name}</h3>
                    <div className="flex flex-wrap gap-2 mt-1 text-sm text-muted-foreground">
                      <span>{formatDate(activity.start_date)}</span>
                      <span>•</span>
                      <span>{formatTime(activity.start_date)}</span>
                      <span>•</span>
                      <span className="capitalize">{activity.platform}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mt-4 md:mt-0 md:ml-4">
                    <div className="text-center">
                      <div className="text-xs text-muted-foreground">
                        Distance
                      </div>
                      <div className="font-semibold">
                        {activity.distance_meters
                          ? formatDistance(activity.distance_meters)
                          : "-"}
                      </div>
                    </div>

                    <div className="text-center">
                      <div className="text-xs text-muted-foreground">Pace</div>
                      <div className="font-semibold">
                        {activity.distance_meters &&
                        activity.moving_time_seconds
                          ? formatPace(
                              activity.moving_time_seconds /
                                60 /
                                (activity.distance_meters / 1000),
                            )
                          : "-"}
                      </div>
                    </div>

                    <div className="text-center">
                      <div className="text-xs text-muted-foreground">
                        Duration
                      </div>
                      <div className="font-semibold">
                        {formatDuration(
                          activity.moving_time_seconds ||
                            activity.elapsed_time_seconds,
                        )}
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
