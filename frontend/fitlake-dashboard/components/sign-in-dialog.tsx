"use client";

import { useEffect } from "react";
import { SignIn } from "@clerk/nextjs";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { dark } from "@clerk/themes";
import { useAuth } from "@clerk/nextjs";

interface SignInDialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  trigger?: React.ReactNode;
}

export function SignInDialog({
  open,
  onOpenChange,
  trigger,
}: SignInDialogProps = {}) {
  const isControlled = open !== undefined;
  const { isSignedIn } = useAuth();

  // Close the dialog as soon as Clerk reports the user is signed in
  useEffect(() => {
    if (isSignedIn && open) {
      onOpenChange?.(false);
    }
  }, [isSignedIn, open, onOpenChange]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {!isControlled && (
        <DialogTrigger asChild>
          {trigger ?? (
            <Button variant="outline" size="sm">
              Sign in
            </Button>
          )}
        </DialogTrigger>
      )}
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
