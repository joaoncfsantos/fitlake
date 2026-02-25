"use client";

import Link from "next/link";
import { PageLayout } from "@/components/page-layout";
import { Heart, Activity, Dumbbell, ArrowUpRight } from "lucide-react";
import { Spotlight } from "@/components/ui/spotlight-new";

import { useRouter } from "next/navigation";
import { useDemoMode } from "@/contexts/demo-mode";

const sections = [
  {
    title: "Health",
    tag: "garmin",
    description:
      "Heart rate, sleep, stress, body battery, steps and training readiness.",
    href: "/health/all",
    icon: Heart,
  },
  {
    title: "Running",
    tag: "strava",
    description: "Running activities with pace, distance, and heart rate data.",
    href: "/running/all",
    icon: Activity,
  },
  {
    title: "Workouts",
    tag: "hevy",
    description: "Strength sessions with exercises, sets, and volume tracking.",
    href: "/workouts/all",
    icon: Dumbbell,
  },
];

export default function Page() {
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
    <PageLayout spotlight={<Spotlight duration={8} xOffset={80} />}>
      <div className="flex flex-col items-center text-center pt-10 pb-6">
        <p className="text-xs font-mono uppercase tracking-[0.3em] text-primary mb-4">
          fitness data lake
        </p>
        <h2 className="text-4xl sm:text-5xl font-bold tracking-tight leading-tight">
          Fitlake
          <br />
          <span className="text-muted-foreground">Your data. One place.</span>
        </h2>
        <p className="mt-5 text-muted-foreground max-w-md text-sm leading-relaxed">
          Fitlake aggregates fitness data from Garmin, Strava, and Hevy into a
          single, unified dashboard.
        </p>
      </div>

      <div className="grid gap-px md:grid-cols-3 border border-border bg-border mt-4">
        {sections.map((section) => (
          <Link
            key={section.href}
            href={section.href}
            className="group relative bg-background p-8 flex flex-col gap-5 transition-colors hover:bg-black/40"
          >
            <div className="flex items-center justify-between">
              <div className="flex h-10 w-10 items-center justify-center border border-primary/30 text-primary">
                <section.icon className="h-4 w-4" />
              </div>
              <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 -translate-y-1 translate-x-1 transition-all group-hover:opacity-100 group-hover:translate-y-0 group-hover:translate-x-0" />
            </div>

            <div className="flex flex-col gap-1.5">
              <h3 className="text-base font-semibold tracking-tight">
                {section.title}
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                {section.description}
              </p>
            </div>

            <span className="mt-auto text-[10px] font-mono uppercase tracking-widest text-muted-foreground/60">
              {section.tag}
            </span>
          </Link>
        ))}
      </div>

      <div className="flex items-center justify-center gap-8 pt-10 pb-4 text-[11px] font-mono uppercase tracking-widest text-muted-foreground/50">
        <span>Garmin</span>
        <span className="h-3 w-px bg-border" />
        <span>Strava</span>
        <span className="h-3 w-px bg-border" />
        <span>Hevy</span>
      </div>
      <button onClick={handleDemo}>
        {!isDemo ? "View Demo" : "Exit Demo"}
      </button>
    </PageLayout>
  );
}
