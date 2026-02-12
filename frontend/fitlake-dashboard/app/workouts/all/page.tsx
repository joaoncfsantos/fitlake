"use client"

import { PageLayout } from "@/components/page-layout"

export default function WorkoutsAllPage() {
  return (
    <PageLayout 
      title="Workouts - All Activities" 
      breadcrumbs={[{ label: "Workouts", href: "/workouts/all" }, { label: "All" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Total Workouts</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Total Volume</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Training Frequency</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 flex items-center justify-center">
        <p className="text-muted-foreground">Workout Activities List</p>
      </div>
    </PageLayout>
  )
}
