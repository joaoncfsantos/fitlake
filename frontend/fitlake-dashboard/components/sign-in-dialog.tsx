"use client";

import { SignIn } from "@clerk/nextjs";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { dark } from "@clerk/themes";

export function SignInDialog() {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          Sign in
        </Button>
      </DialogTrigger>
      <DialogContent className="p-0 bg-transparent shadow-none ring-0 [&>button]:hidden">
        <DialogTitle className="hidden"></DialogTitle>
        <SignIn
          routing="hash"
          appearance={{
            baseTheme: dark,
            variables: {
              colorBackground: "var(--background)",
              colorPrimary: "var(--primary)",
              borderRadius: "var(--radius)",
              fontFamily: "var(--font-sans)",
            },
          }}
        />
      </DialogContent>
    </Dialog>
  );
}
