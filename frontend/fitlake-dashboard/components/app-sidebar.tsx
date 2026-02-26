"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

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
} from "@/components/ui/sidebar";

const data = {
  navMain: [
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
      ],
    },
  ],
};

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname();

  return (
    <Sidebar {...props}>
      <SidebarHeader>
        <Link href="/">
          <p className="text-2xl font-bold px-2 cursor-pointer">Fitlake</p>
        </Link>
      </SidebarHeader>
      <SidebarContent>
        {data.navMain.map((item) => (
          <SidebarGroup key={item.title}>
            <SidebarGroupLabel className="text-xs font-semibold uppercase tracking-widest text-sidebar-foreground border-t border-sidebar-border pt-2">
              {item.title}
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {item.items.map((subItem) => (
                  <SidebarMenuItem key={subItem.title}>
                    <SidebarMenuButton
                      asChild
                      isActive={pathname === subItem.url}
                    >
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
  );
}
