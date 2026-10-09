import React, { createContext, useContext, useState, useEffect } from "react";
import { api } from "../services/api";

interface User {
  id: string;
  username: string;
  email: string;
  role: "officer" | "borrower";
  full_name: string;
  is_demo_user: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (u: string, p: string) => Promise<void>;
  signup: (data: any) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem("credence_token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      api.getMe()
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {
          logout();
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [token]);

  const login = async (u: string, p: string) => {
    const res = await api.login(u, p);
    localStorage.setItem("credence_token", res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  };

  const signup = async (data: any) => {
    const res = await api.signup(data);
    localStorage.setItem("credence_token", res.access_token);
    setToken(res.access_token);
    setUser(res.user);
  };

  const logout = () => {
    localStorage.removeItem("credence_token");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
};
