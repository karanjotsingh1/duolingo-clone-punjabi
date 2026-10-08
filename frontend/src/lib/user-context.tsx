"use client";
import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "./api";
import type { UserState } from "./types";

type Ctx = {
  user: UserState | null;
  error: string | null;
  refresh: () => Promise<void>;
  setUser: (u: UserState) => void;     // push a fresh snapshot returned by a mutating API call
};
const UserContext = createContext<Ctx>({ user: null, error: null, refresh: async () => {}, setUser: () => {} });

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserState | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try { setUser(await api.me()); setError(null); }
    catch { setError("Could not reach the server. Is the backend running?"); }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  // Re-poll once a minute so the heart-regeneration timer stays accurate.
  useEffect(() => {
    const t = setInterval(refresh, 60_000);
    return () => clearInterval(t);
  }, [refresh]);

  return <UserContext.Provider value={{ user, error, refresh, setUser }}>{children}</UserContext.Provider>;
}

export const useUser = () => useContext(UserContext);
