"use client"

import { PageLayout } from "@/components/page-layout"

export default function TrainingReadinessPage() {
  return (
    <PageLayout 
      title="Training Readiness" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Training Readiness" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-2">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Readiness Score</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Recovery Status</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 flex items-center justify-center">
        <p className="text-muted-foreground">Training Readiness Trends</p>
      </div>
    </PageLayout>
  )
}
