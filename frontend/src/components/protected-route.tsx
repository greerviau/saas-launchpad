"use client";

import { useAuth } from "@/contexts/auth-context";
import { useUser } from "@/contexts/user-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function ProtectedRoute({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const { userData, isLoading: userLoading } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [authLoading, isAuthenticated, router]);

  if (authLoading || userLoading) {
    return <div>Loading...</div>;
  }

  if (!userData) {
    return null;
  }

  return <>{children}</>;
}
