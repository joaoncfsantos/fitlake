"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"

import { SearchForm } from "@/components/search-form"
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"



const data = {
  navMain: [
    {
      title: "Overview",
      items: [
        {
          title: "Overview",
          url: "/overview",
        },
      ],
    },
    {
      title: "Health",
      items: [
        {
          title: "All",
          url: "/health/all",
        },
        {
          title: "Body Battery",
          url: "/health/body-battery",
        },
        {
          title: "Heart Rate",
          url: "/health/heart-rate",
        },
        {
          title: "Sleep",
          url: "/health/sleep",
        },
        {
          title: "Steps",
          url: "/health/steps",
        },
        {
          title: "Stress",
          url: "/health/stress",
        },
        {
          title: "Training Readiness",
          url: "/health/training-readiness",
        },
      ],
    },
    {
      title: "Running",
      items: [
        {
          title: "All",
          url: "/running/all",
        },
      ],
    },
    {
      title: "Workouts",
      items: [
        {
          title: "All",
          url: "/workouts/all",
        },
        {
          title: "Muscle Distribution",
          url: "/workouts/muscle-distribution",
        },
        {
          title: "Set Count Per Muscle Group",
          url: "/workouts/set-count-per-muscle-group",
        },
        {
          title: "Training Load",
          url: "/workouts/training-load",
        },
      ],
    },
    
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname()
  
  return (
    <Sidebar {...props}>
      <SidebarHeader>
        <p className="text-xl font-bold px-2">Fitlake Dashboard</p>
        <SearchForm />
      </SidebarHeader>
      <SidebarContent>
        {data.navMain.map((item) => (
          <SidebarGroup key={item.title}>
            <SidebarGroupLabel>{item.title}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {item.items.map((subItem) => (
                  <SidebarMenuItem key={subItem.title}>
                    <SidebarMenuButton asChild isActive={pathname === subItem.url}>
                      <Link href={subItem.url}>{subItem.title}</Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  )
}
