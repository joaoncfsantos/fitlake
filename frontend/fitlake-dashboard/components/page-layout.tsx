"use client";

import * as React from "react";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { SignInDialog } from "./sign-in-dialog";
import { DemoBanner } from "./demo-banner";
import { useDemoMode } from "@/contexts/demo-mode";
import { useRouter } from "next/navigation";

import { ClerkLoading } from "@clerk/nextjs";
import { Button } from "./ui/button";

interface PageLayoutProps {
  title?: string;
  breadcrumbs?: { label: string; href?: string }[];
  children: React.ReactNode;
  action?: React.ReactNode;
  spotlight?: React.ReactNode;
}

export function PageLayout({
  title,
  breadcrumbs = [],
  children,
  action,
  spotlight,
}: PageLayoutProps) {
  const { enableDemo, disableDemo, isDemo } = useDemoMode();
  const router = useRouter();

  const handleDemo = () => {
    if (isDemo) {
      disableDemo();
      router.push("/");
    } else {
      enableDemo();
      router.push("/health/all");
    }
  };

  return (
    <SidebarInset className={spotlight ? "overflow-hidden" : undefined}>
      {spotlight}
      <DemoBanner />
      <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
        <SidebarTrigger className="-ml-1" />
        <Separator
          orientation="vertical"
          className="mr-2 data-[orientation=vertical]:h-4"
        />
        {breadcrumbs.length > 0 && (
          <Breadcrumb>
            <BreadcrumbList>
              <BreadcrumbItem className="hidden md:block">
                <BreadcrumbLink href="/">Fitlake Dashboard</BreadcrumbLink>
              </BreadcrumbItem>
              {breadcrumbs.map((crumb, index) => (
                <React.Fragment key={index}>
                  <BreadcrumbSeparator className="hidden md:block" />
                  <BreadcrumbItem>
                    {crumb.href ? (
                      <BreadcrumbLink href={crumb.href}>
                        {crumb.label}
                      </BreadcrumbLink>
                    ) : (
                      <BreadcrumbPage>{crumb.label}</BreadcrumbPage>
                    )}
                  </BreadcrumbItem>
                </React.Fragment>
              ))}
            </BreadcrumbList>
          </Breadcrumb>
        )}

        <div className="ml-auto flex items-center gap-2">
          <button
            className="relative after:absolute after:left-0 after:bottom-0 after:w-full after:scale-x-0 after:h-px after:bg-current after:transition-transform after:duration-200 hover:after:scale-x-100 overflow-hidden"
            onClick={handleDemo}
          >
            {!isDemo ? "View Demo" : "Exit Demo"}
          </button>
          <span className="cursor-default">or</span>
          <ClerkLoading>
            <Button variant="outline" size="sm" disabled className="opacity-0">
              Sign in
            </Button>
          </ClerkLoading>
          <SignedOut>
            <SignInDialog />
          </SignedOut>
          <SignedIn>
            <UserButton />
          </SignedIn>
        </div>
      </header>
      <div className="flex flex-1 flex-col gap-4 p-4">
        <div className="flex items-center justify-between">
          {title && <h1 className="text-3xl font-bold">{title}</h1>}
          {action && <div>{action}</div>}
        </div>
        {children}
      </div>
    </SidebarInset>
  );
}
