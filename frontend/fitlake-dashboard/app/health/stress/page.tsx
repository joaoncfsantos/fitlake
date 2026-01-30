"use client"

import { PageLayout } from "@/components/page-layout"

export default function StressPage() {
  return (
    <PageLayout 
      title="Stress" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Stress" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Current Stress Level</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Average Stress</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Rest Time</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 flex items-center justify-center">
        <p className="text-muted-foreground">Stress Level History Chart</p>
      </div>
    </PageLayout>
  )
}
