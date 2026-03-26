"use client";

import { PageLayout } from "@/components/page-layout";
import { useRunningActivities } from "@/hooks/useRunningActivities";
import { useActivityDetail } from "@/hooks/useActivityDetail";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { RefreshCw } from "lucide-react";
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

export default function RunningAllPage() {
  const {
    data: activities,
    loading,
    error,
    refetch,
  } = useRunningActivities(100);
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState<string | null>(null);
  const [selectedActivityId, setSelectedActivityId] = useState<number | null>(
    null,
  );
  const {
    data: activityDetail,
    loading: detailLoading,
    error: detailError,
  } = useActivityDetail(selectedActivityId);

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

  const formatElevation = (meters: number | null | undefined) => {
    if (meters == null || Number.isNaN(meters)) return "—";
    return `${Math.round(meters)} m`;
  };

  const formatSpeedKmh = (mps: number | null | undefined) => {
    if (mps == null || Number.isNaN(mps)) return "—";
    return `${(mps * 3.6).toFixed(1)} km/h`;
  };

  const paceFromActivity = (
    distanceM: number | null | undefined,
    movingSec: number | null | undefined,
    elapsedSec: number,
  ) => {
    const dist = distanceM ?? 0;
    const timeSec = movingSec ?? elapsedSec;
    if (dist <= 0 || timeSec <= 0) return null;
    return timeSec / 60 / (dist / 1000);
  };

  const activityPace = (a: {
    distance_meters?: number | null;
    moving_time_seconds?: number | null;
    elapsed_time_seconds: number;
  }) =>
    paceFromActivity(
      a.distance_meters,
      a.moving_time_seconds,
      a.elapsed_time_seconds,
    );

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
                  role="button"
                  tabIndex={0}
                  onClick={() => setSelectedActivityId(activity.id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setSelectedActivityId(activity.id);
                    }
                  }}
                  className="flex flex-col md:flex-row md:items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-ring"
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
                        {(() => {
                          const p = activityPace(activity);
                          return p != null ? formatPace(p) : "-";
                        })()}
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

      <Dialog
        open={selectedActivityId !== null}
        onOpenChange={(open) => {
          if (!open) setSelectedActivityId(null);
        }}
      >
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto gap-4">
          <DialogHeader>
            <DialogTitle>{activityDetail?.name ?? "Run"}</DialogTitle>
            <DialogDescription asChild>
              <div className="flex flex-wrap gap-x-3 gap-y-1 text-muted-foreground">
                {activityDetail && (
                  <>
                    <span>{formatDate(activityDetail.start_date)}</span>
                    <span>{formatTime(activityDetail.start_date)}</span>
                    <span className="capitalize">{activityDetail.platform}</span>
                    <span>{activityDetail.activity_type}</span>
                    {activityDetail.sport_type &&
                      activityDetail.sport_type !==
                        activityDetail.activity_type && (
                        <span className="capitalize">
                          {activityDetail.sport_type}
                        </span>
                      )}
                  </>
                )}
              </div>
            </DialogDescription>
          </DialogHeader>

          {detailLoading && (
            <div className="space-y-3">
              <Skeleton className="h-16 w-full rounded-lg" />
              <Skeleton className="h-16 w-full rounded-lg" />
            </div>
          )}

          {detailError && (
            <div className="bg-destructive/10 text-destructive p-3 rounded-lg text-sm">
              {detailError.message}
            </div>
          )}

          {!detailLoading && !detailError && activityDetail && (
            <div className="space-y-4">
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3 text-sm">
                <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                  <dt className="text-muted-foreground">Distance</dt>
                  <dd className="font-medium tabular-nums text-right">
                    {activityDetail.distance_meters != null
                      ? formatDistance(activityDetail.distance_meters)
                      : "—"}
                  </dd>
                </div>
                <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                  <dt className="text-muted-foreground">Pace</dt>
                  <dd className="font-medium tabular-nums text-right">
                    {(() => {
                      const p = activityPace(activityDetail);
                      return p != null ? formatPace(p) : "—";
                    })()}
                  </dd>
                </div>
                <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                  <dt className="text-muted-foreground">Moving time</dt>
                  <dd className="font-medium tabular-nums text-right">
                    {activityDetail.moving_time_seconds != null
                      ? formatDuration(activityDetail.moving_time_seconds)
                      : "—"}
                  </dd>
                </div>
                <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                  <dt className="text-muted-foreground">Elapsed time</dt>
                  <dd className="font-medium tabular-nums text-right">
                    {formatDuration(activityDetail.elapsed_time_seconds)}
                  </dd>
                </div>
                <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                  <dt className="text-muted-foreground">Avg speed</dt>
                  <dd className="font-medium tabular-nums text-right">
                    {formatSpeedKmh(activityDetail.average_speed_mps)}
                  </dd>
                </div>
                <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                  <dt className="text-muted-foreground">Max speed</dt>
                  <dd className="font-medium tabular-nums text-right">
                    {formatSpeedKmh(activityDetail.max_speed_mps)}
                  </dd>
                </div>
                <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                  <dt className="text-muted-foreground">Elevation gain</dt>
                  <dd className="font-medium tabular-nums text-right">
                    {formatElevation(
                      activityDetail.total_elevation_gain_meters,
                    )}
                  </dd>
                </div>
                <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                  <dt className="text-muted-foreground">Elev. high / low</dt>
                  <dd className="font-medium tabular-nums text-right">
                    {activityDetail.elevation_high_meters != null ||
                    activityDetail.elevation_low_meters != null
                      ? `${formatElevation(activityDetail.elevation_high_meters)} / ${formatElevation(activityDetail.elevation_low_meters)}`
                      : "—"}
                  </dd>
                </div>
                <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                  <dt className="text-muted-foreground">Avg heart rate</dt>
                  <dd className="font-medium tabular-nums text-right">
                    {activityDetail.average_heartrate != null
                      ? `${Math.round(activityDetail.average_heartrate)} bpm`
                      : "—"}
                  </dd>
                </div>
                <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                  <dt className="text-muted-foreground">Max heart rate</dt>
                  <dd className="font-medium tabular-nums text-right">
                    {activityDetail.max_heartrate != null
                      ? `${Math.round(activityDetail.max_heartrate)} bpm`
                      : "—"}
                  </dd>
                </div>
                <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                  <dt className="text-muted-foreground">Calories</dt>
                  <dd className="font-medium tabular-nums text-right">
                    {activityDetail.calories != null
                      ? `${Math.round(activityDetail.calories)} kcal`
                      : "—"}
                  </dd>
                </div>
                {(activityDetail.average_watts != null ||
                  activityDetail.max_watts != null) && (
                  <>
                    <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                      <dt className="text-muted-foreground">Avg power</dt>
                      <dd className="font-medium tabular-nums text-right">
                        {activityDetail.average_watts != null
                          ? `${Math.round(activityDetail.average_watts)} W`
                          : "—"}
                      </dd>
                    </div>
                    <div className="flex justify-between gap-4 border-b border-border/60 pb-2 sm:border-0 sm:pb-0">
                      <dt className="text-muted-foreground">Max power</dt>
                      <dd className="font-medium tabular-nums text-right">
                        {activityDetail.max_watts != null
                          ? `${Math.round(activityDetail.max_watts)} W`
                          : "—"}
                      </dd>
                    </div>
                  </>
                )}
              </dl>

              {activityDetail.description?.trim() && (
                <div className="rounded-lg border bg-muted/30 p-3 text-sm">
                  <p className="text-xs font-medium text-muted-foreground mb-1">
                    Description
                  </p>
                  <p className="text-foreground whitespace-pre-wrap">
                    {activityDetail.description}
                  </p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </PageLayout>
  );
}
