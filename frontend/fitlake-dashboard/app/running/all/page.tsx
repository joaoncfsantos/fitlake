"use client"

import { PageLayout } from "@/components/page-layout"

export default function RunningAllPage() {
  return (
    <PageLayout 
      title="Running - All Activities" 
      breadcrumbs={[{ label: "Running", href: "/running/all" }, { label: "All" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Total Distance</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Average Pace</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Total Time</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 flex items-center justify-center">
        <p className="text-muted-foreground">Running Activities List</p>
      </div>
    </PageLayout>
  )
}
