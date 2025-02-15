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

  const login = useCallback(
    (token: string) => {
      setAccessToken(token);
      setIsAuthenticated(true);
      router.push("/dashboard");
    },
    [router]
  );

  const logout = useCallback(async () => {
    try {
      await api.post("/users/logout");
    } catch (error) {
      console.error("Failed to logout:", error);
    } finally {
      setAccessToken(null);
      setIsAuthenticated(false);
      router.push("/login");
    }
  }, [router]);

  const refreshTokenFn = useCallback(async () => {
    try {
      const response = await api.get("/users/refresh");
      const { token } = response.data;

      setAccessToken(token);
      setIsAuthenticated(true);
      setIsLoading(false);
      console.log("User is authenticated");
      return token;
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
    const responseInterceptor = api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;

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
          } catch (refreshError) {
            console.error("Refresh token failed:", refreshError);
            await logout();
            return Promise.reject(refreshError);
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.response.eject(responseInterceptor);
    };
  }, [refreshTokenFn]);

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
