"use client"

import { PageLayout } from "@/components/page-layout"

export default function HealthAllPage() {
  return (
    <PageLayout 
      title="Health - All Metrics" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "All" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Body Battery</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Heart Rate</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Sleep</p>
        </div>
      </div>
      <div className="grid auto-rows-min gap-4 md:grid-cols-3 mt-4">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Steps</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Stress</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Training Readiness</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 flex items-center justify-center">
        <p className="text-muted-foreground">Comprehensive Health Dashboard</p>
      </div>
    </PageLayout>
  )
}
