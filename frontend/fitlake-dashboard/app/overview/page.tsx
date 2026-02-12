"use client"

import { PageLayout } from "@/components/page-layout"

export default function OverviewPage() {
  return (
    <PageLayout 
      title="Overview" 
      breadcrumbs={[{ label: "Overview" }]}
    >
      <div className="grid auto-rows-min gap-4 md:grid-cols-3">
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Chart 1</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Chart 2</p>
        </div>
        <div className="bg-muted/50 aspect-video rounded-xl flex items-center justify-center">
          <p className="text-muted-foreground">Chart 3</p>
        </div>
      </div>
      <div className="bg-muted/50 min-h-[100vh] flex-1 rounded-xl md:min-h-min flex items-center justify-center">
        <p className="text-muted-foreground">Main Content Area</p>
      </div>
    </PageLayout>
  )
}
