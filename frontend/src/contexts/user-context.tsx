"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { api, useAuth } from "./auth-context";

interface User {
  id: string;
  email: string;
  name: string;
  has_access: boolean;
  // Add other user properties as needed
}

interface UserContextType {
  userData: User | null;
  refreshUser: () => void;
  isLoading: boolean;
  hasAccess: boolean | null;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [userData, setUserData] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasAccess, setHasAccess] = useState<boolean | null>(null);

  const refreshUser = useCallback(async () => {
    try {
      const { data } = await api.get("/users/whoami");
      setUserData(data);
      setHasAccess(data.has_access);
    } catch (error) {
      console.error("Failed to fetch user:", error);
      setUserData(null);
      setHasAccess(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      refreshUser();
      setIsLoading(false);
    } else if (isAuthenticated === false) {
      setUserData(null);
      setHasAccess(false);
      setIsLoading(false);
    }
  }, [refreshUser, isAuthenticated]);

  const value = useMemo(
    () => ({
      userData,
      refreshUser,
      isLoading,
      hasAccess,
    }),
    [userData, refreshUser, isLoading, hasAccess]
  );

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
};
