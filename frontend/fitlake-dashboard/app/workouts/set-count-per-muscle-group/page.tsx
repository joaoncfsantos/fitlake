"use client"

import { PageLayout } from "@/components/page-layout"

export default function SetCountPerMuscleGroupPage() {
  return (
    <PageLayout 
      title="Set Count Per Muscle Group" 
      breadcrumbs={[{ label: "Workouts", href: "/workouts/all" }, { label: "Set Count Per Muscle Group" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-2">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Weekly Volume</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Volume Distribution</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 flex items-center justify-center">
        <p className="text-muted-foreground">Set Count by Muscle Group Chart</p>
      </div>
    </PageLayout>
  )
}
