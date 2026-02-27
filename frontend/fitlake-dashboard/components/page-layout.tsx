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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { SignedIn, SignedOut, useAuth, UserButton } from "@clerk/nextjs";
import { SignInDialog } from "./sign-in-dialog";
import { DemoBanner } from "./demo-banner";
import { useDemoMode } from "@/contexts/demo-mode";
import { useRouter } from "next/navigation";

import { ClerkLoading } from "@clerk/nextjs";
import { Button } from "./ui/button";
import { useInsight } from "@/hooks/useInsight";

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
  const { isSignedIn } = useAuth();
  const [signInOpen, setSignInOpen] = React.useState(false);

  const handleDemo = () => {
    if (isDemo) {
      if (isSignedIn) {
        disableDemo();
        router.push("/");
      } else {
        setSignInOpen(true);
      }
    } else {
      enableDemo();
      router.push("/health/all");
    }
  };

  const { data: insight, error, isLoading } = useInsight();
  const [insightOpen, setInsightOpen] = React.useState(false);

  const getInsight = () => {
    if (insight) {
      setInsightOpen(true);
      console.log(insight);
    } else {
      console.error(error);
    }
  };

  return (
    <>
      <SidebarInset>
        {spotlight && (
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {spotlight}
          </div>
        )}
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
                    <BreadcrumbSeparator
                      className={index === 0 ? "hidden md:block" : ""}
                    />
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
            {isSignedIn && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  getInsight();
                }}
              >
                Get Insight
              </Button>
            )}
            <ClerkLoading>
              <Button
                variant="outline"
                size="sm"
                disabled
                className="opacity-0"
              >
                Sign in
              </Button>
            </ClerkLoading>
            <SignedOut>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSignInOpen(true)}
              >
                Sign in
              </Button>
            </SignedOut>
            <SignedIn>
              <UserButton />
            </SignedIn>
          </div>
        </header>
        <SignInDialog open={signInOpen} onOpenChange={setSignInOpen} />
        <div className="flex flex-1 flex-col gap-4 p-4">
          <div className="flex items-center justify-between">
            {title && <h1 className="text-3xl font-bold">{title}</h1>}
            {action && <div>{action}</div>}
          </div>
          {children}
        </div>
      </SidebarInset>
      <Dialog open={insightOpen} onOpenChange={setInsightOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>AI Insight</DialogTitle>
            <DialogDescription>
              {insight?.insight || "No insight available"}
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </>
  );
}
