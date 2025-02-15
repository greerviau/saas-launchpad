"use client";

import axios from "axios";
import { useRouter } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useLayoutEffect,
  useMemo,
  useState,
} from "react";

interface AuthContextType {
  isAuthenticated: boolean | null;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Update the axios instance to use relative URLs
export const api = axios.create({
  // Remove the baseURL since we're using the proxy
  // The proxy will automatically forward requests to the backend
  baseURL: "/api",
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const router = useRouter();

  const login = useCallback((token: string) => {
    setAccessToken(token);
    setIsAuthenticated(true);
  }, []);

  const logout = useCallback(async () => {
    console.log("log out");
    try {
      await api.post("/users/logout");
    } catch (error) {
      console.error("Failed to logout:", error);
    } finally {
      setAccessToken(null);
      setIsAuthenticated(false);
      router.push("/login");
    }
  }, []);

  const refreshTokenFn = useCallback(async () => {
    try {
      const { data } = await api.get("/users/refresh");
      setIsAuthenticated(true);
      setAccessToken(data.token);
      setIsLoading(false);
      console.log("User is authenticated");
      return data.token;
    } catch (error) {
      console.error("Failed to refresh token:", error);
      setIsAuthenticated(false);
      setAccessToken(null);
      setIsLoading(false);
      return null;
    }
  }, []);

  useEffect(() => {
    refreshTokenFn();
  }, [refreshTokenFn]);

  // Add request interceptor to add bearer token
  useLayoutEffect(() => {
    const requestInterceptor = api.interceptors.request.use(
      (config) => {
        if (accessToken) {
          config.headers.Authorization = `Bearer ${accessToken}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.request.eject(requestInterceptor);
    };
  }, [accessToken]);

  useLayoutEffect(() => {
    const refreshInterceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

        // Skip refresh token logic for refresh and logout endpoints
        if (
          originalRequest.url === "/users/refresh" ||
          originalRequest.url === "/users/logout" ||
          originalRequest.url === "/users/login"
        ) {
          return Promise.reject(error);
        }

        // Handle rate limiting (429) separately
        if (error.response?.status === 429) {
          console.error("Rate limit exceeded:", error.response?.data);
          return Promise.reject(error);
        }
        // Only attempt refresh for 401 errors
        if (error.response?.status === 401 && !originalRequest._retry) {
          try {
            originalRequest._retry = true;

            const token = await refreshTokenFn();
            if (!token) {
              throw new Error("Failed to refresh token");
            }
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          } catch (error) {
            console.error("Failed to refresh token:", error);
            await logout();
            return Promise.reject(error);
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.response.eject(refreshInterceptor);
    };
  }, [refreshTokenFn, logout]);

  // Update the Provider value using useMemo for better performance
  const authContextValue = useMemo(
    () => ({
      isAuthenticated,
      isLoading,
      login,
      logout,
    }),
    [isAuthenticated, isLoading, login, logout]
  );

  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
