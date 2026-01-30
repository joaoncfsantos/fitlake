"use client"

import { PageLayout } from "@/components/page-layout"

export default function SleepPage() {
  return (
    <PageLayout 
      title="Sleep" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Sleep" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Total Sleep Time</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Sleep Quality</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">REM Sleep</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 flex items-center justify-center">
        <p className="text-muted-foreground">Sleep Stages Chart</p>
      </div>
    </PageLayout>
  )
}
