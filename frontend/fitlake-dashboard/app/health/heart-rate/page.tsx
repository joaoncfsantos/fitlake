"use client"

import { PageLayout } from "@/components/page-layout"

export default function HeartRatePage() {
  return (
    <PageLayout 
      title="Heart Rate" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Heart Rate" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Current HR</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Resting HR</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Max HR</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 flex items-center justify-center">
        <p className="text-muted-foreground">Heart Rate History Chart</p>
      </div>
    </PageLayout>
  )
}
