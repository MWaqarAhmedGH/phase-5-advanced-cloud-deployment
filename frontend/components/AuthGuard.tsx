"use client";

import { useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { isTokenValid } from "@/lib/auth-utils";

interface AuthGuardProps {
  children: ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    if (!isTokenValid()) {
      localStorage.removeItem("auth_token");
      router.push("/signin");
      return;
    }
    setIsAuthenticated(true);
  }, [router]);

  if (isAuthenticated === null) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-700">
        <div className="text-center">
          <div className="relative">
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-emerald-500 to-blue-500 blur-lg opacity-40 animate-pulse"></div>
            <svg
              className="relative w-12 h-12 spinner-glow"
              viewBox="0 0 24 24"
              fill="none"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="url(#aurora-grad)"
                strokeWidth="3"
              />
              <path
                className="opacity-75"
                fill="url(#aurora-grad)"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
              <defs>
                <linearGradient id="aurora-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#10b981" />
                  <stop offset="100%" stopColor="#3b82f6" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <p className="mt-4 text-sm text-slate-400">Authenticating...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
