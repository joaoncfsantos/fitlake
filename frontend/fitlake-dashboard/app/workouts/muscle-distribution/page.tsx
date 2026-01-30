"use client"

import { PageLayout } from "@/components/page-layout"

export default function MuscleDistributionPage() {
  return (
    <PageLayout 
      title="Muscle Distribution" 
      breadcrumbs={[{ label: "Workouts", href: "/workouts/all" }, { label: "Muscle Distribution" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-2">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Muscle Group Breakdown</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Training Balance</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 flex items-center justify-center">
        <p className="text-muted-foreground">Muscle Distribution Chart</p>
      </div>
    </PageLayout>
  )
}
