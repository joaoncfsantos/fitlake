"use client"

import { PageLayout } from "@/components/page-layout"

export default function TrainingLoadPage() {
  return (
    <PageLayout 
      title="Training Load" 
      breadcrumbs={[{ label: "Workouts", href: "/workouts/all" }, { label: "Training Load" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Acute Load</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Chronic Load</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Load Ratio</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 flex items-center justify-center">
        <p className="text-muted-foreground">Training Load Trends</p>
      </div>
    </PageLayout>
  )
}
