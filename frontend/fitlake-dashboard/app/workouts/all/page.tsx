"use client";

import { PageLayout } from "@/components/page-layout";
import { useWorkouts } from "@/hooks/useWorkouts";
import { useWorkoutDetail } from "@/hooks/useWorkoutDetail";
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
import {
  exerciseVolumeKg,
  setVolumeKg,
  workoutVolumeKg,
} from "@/lib/workout-volume";

export default function WorkoutsAllPage() {
  const { data: workouts, loading, error, refetch } = useWorkouts(100);
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState<string | null>(null);
  const [selectedWorkoutId, setSelectedWorkoutId] = useState<number | null>(
    null,
  );
  const {
    data: workoutDetail,
    loading: detailLoading,
    error: detailError,
  } = useWorkoutDetail(selectedWorkoutId);

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

  const formatWeightKg = (kg: number | null | undefined) => {
    if (kg == null || Number.isNaN(kg)) return "—";
    return `${kg} kg`;
  };

  const formatReps = (reps: number | null | undefined) => {
    if (reps == null || Number.isNaN(reps)) return "—";
    return String(reps);
  };

  const formatSetType = (type: string | undefined) => {
    if (!type) return "Normal";
    return type;
  };

  /** Σ(weight × reps); displayed as kg (tonnage). */
  const formatVolumeKg = (kg: number) => {
    if (kg <= 0) return "0 kg";
    const rounded = Math.round(kg * 100) / 100;
    return `${rounded.toLocaleString()} kg`;
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
                  role="button"
                  tabIndex={0}
                  onClick={() => setSelectedWorkoutId(workout.id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setSelectedWorkoutId(workout.id);
                    }
                  }}
                  className="flex flex-col md:flex-row md:items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-ring"
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

      <Dialog
        open={selectedWorkoutId !== null}
        onOpenChange={(open) => {
          if (!open) setSelectedWorkoutId(null);
        }}
      >
        <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto gap-4">
          <DialogHeader>
            <DialogTitle>{workoutDetail?.title ?? "Workout"}</DialogTitle>
            <DialogDescription asChild>
              <div className="flex flex-wrap gap-x-3 gap-y-1 text-muted-foreground">
                {workoutDetail && (
                  <>
                    <span>{formatDate(workoutDetail.start_time)}</span>
                    <span>{formatTime(workoutDetail.start_time)}</span>
                    <span className="capitalize">{workoutDetail.platform}</span>
                    <span>
                      {formatDuration(workoutDetail.duration_seconds)}
                    </span>
                    <span className="font-medium text-foreground">
                      Total volume:{" "}
                      {formatVolumeKg(
                        workoutVolumeKg(workoutDetail.exercises ?? []),
                      )}
                    </span>
                  </>
                )}
              </div>
            </DialogDescription>
          </DialogHeader>

          {detailLoading && (
            <div className="space-y-3">
              <Skeleton className="h-24 w-full rounded-lg" />
              <Skeleton className="h-24 w-full rounded-lg" />
            </div>
          )}

          {detailError && (
            <div className="bg-destructive/10 text-destructive p-3 rounded-lg text-sm">
              {detailError.message}
            </div>
          )}

          {!detailLoading && !detailError && workoutDetail && (
            <div className="rounded-lg border bg-muted/20 p-3 space-y-2">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <span className="text-sm font-medium">Muscle distribution</span>
                <span className="text-sm text-muted-foreground tabular-nums">
                  Total sets: {workoutDetail.total_sets ?? 0}
                </span>
              </div>
              <p className="text-xs text-muted-foreground">
                Weighted sets: primary muscle 1× per set, secondary 0.5× per
                set (same as analytics).
              </p>
              {(workoutDetail.muscle_distribution ?? []).length > 0 ? (
                <div className="rounded-md border overflow-hidden bg-background">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b bg-muted/50 text-left">
                        <th className="px-3 py-2 font-medium">Muscle</th>
                        <th className="px-3 py-2 font-medium text-right tabular-nums">
                          Weighted
                        </th>
                        <th className="px-3 py-2 font-medium text-right tabular-nums w-20">
                          Share
                        </th>
                        <th className="px-3 py-2 font-medium text-right tabular-nums w-18 hidden sm:table-cell">
                          Primary sets
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {(workoutDetail.muscle_distribution ?? []).map((row) => (
                        <tr key={row.muscle_group} className="border-b last:border-0">
                          <td className="px-3 py-2 capitalize">
                            {row.muscle_group.replace(/_/g, " ")}
                          </td>
                          <td className="px-3 py-2 text-right tabular-nums">
                            {row.weighted_sets.toLocaleString(undefined, {
                              maximumFractionDigits: 2,
                            })}
                          </td>
                          <td className="px-3 py-2 text-right tabular-nums text-muted-foreground">
                            {row.percentage.toFixed(1)}%
                          </td>
                          <td className="px-3 py-2 text-right tabular-nums text-muted-foreground hidden sm:table-cell">
                            {row.total_sets}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-xs text-muted-foreground">
                  No muscle breakdown for this session — exercises need
                  matching templates in the database.
                </p>
              )}
            </div>
          )}

          {!detailLoading &&
            !detailError &&
            workoutDetail &&
            (workoutDetail.exercises ?? []).length === 0 && (
              <p className="text-sm text-muted-foreground">
                No exercises recorded for this workout.
              </p>
            )}

          {!detailLoading &&
            !detailError &&
            workoutDetail &&
            (workoutDetail.exercises ?? []).length > 0 && (
              <div className="space-y-6">
                {(workoutDetail.exercises ?? []).map((exercise, exIdx) => {
                  const sets = exercise.sets ?? [];
                  const title =
                    exercise.title?.trim() ||
                    `Exercise ${(exercise.index ?? exIdx) + 1}`;
                  const exVol = exerciseVolumeKg(exercise);
                  return (
                    <div key={`${title}-${exIdx}`}>
                      <div className="flex flex-wrap items-baseline justify-between gap-2 mb-2">
                        <h4 className="font-medium text-foreground">{title}</h4>
                        {sets.length > 0 && (
                          <span className="text-sm text-muted-foreground tabular-nums">
                            Volume: {formatVolumeKg(exVol)}
                          </span>
                        )}
                      </div>
                      {sets.length === 0 ? (
                        <p className="text-sm text-muted-foreground">
                          No sets logged.
                        </p>
                      ) : (
                        <div className="rounded-md border overflow-hidden">
                          <table className="w-full text-sm">
                            <thead>
                              <tr className="border-b bg-muted/50 text-left">
                                <th className="px-3 py-2 font-medium w-14">
                                  Set
                                </th>
                                <th className="px-3 py-2 font-medium">
                                  Weight
                                </th>
                                <th className="px-3 py-2 font-medium">Reps</th>
                                <th className="px-3 py-2 font-medium tabular-nums">
                                  Volume
                                </th>
                                <th className="px-3 py-2 font-medium w-28 hidden sm:table-cell">
                                  Type
                                </th>
                              </tr>
                            </thead>
                            <tbody>
                              {sets.map((set, setIdx) => {
                                const setLabel =
                                  set.index != null
                                    ? set.index + 1
                                    : setIdx + 1;
                                const typeLabel = formatSetType(set.type);
                                const vol = setVolumeKg(set);
                                return (
                                  <tr
                                    key={`${exIdx}-${setIdx}`}
                                    className="border-b last:border-0"
                                  >
                                    <td className="px-3 py-2 text-muted-foreground">
                                      {setLabel}
                                    </td>
                                    <td className="px-3 py-2 tabular-nums">
                                      {formatWeightKg(set.weight_kg)}
                                    </td>
                                    <td className="px-3 py-2 tabular-nums">
                                      {formatReps(set.reps)}
                                    </td>
                                    <td className="px-3 py-2 tabular-nums text-muted-foreground">
                                      {vol > 0 ? formatVolumeKg(vol) : "—"}
                                    </td>
                                    <td className="px-3 py-2 text-muted-foreground hidden sm:table-cell capitalize">
                                      {typeLabel ?? "—"}
                                    </td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
        </DialogContent>
      </Dialog>
    </PageLayout>
  );
}
