"use client"

import { PageLayout } from "@/components/page-layout"

export default function StepsPage() {
  return (
    <PageLayout 
      title="Steps" 
      breadcrumbs={[{ label: "Health", href: "/health/all" }, { label: "Steps" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Today's Steps</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Daily Average</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Goal Progress</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[50vh] flex-1 rounded-xl mt-4 flex items-center justify-center">
        <p className="text-muted-foreground">Steps History Chart</p>
      </div>
    </PageLayout>
  )
}
