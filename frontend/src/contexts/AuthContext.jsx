// src/contexts/AuthContext.jsx
import { useState, useEffect, useCallback } from 'react';
import { api, getAccessToken, setTokens, clearTokens } from '../services/api';
import { AuthContext } from './auth-context';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Au démarrage : si on a un token, on essaie de charger le profil
  useEffect(() => {
    const bootstrap = async () => {
      const token = getAccessToken();
      if (!token) {
        setIsLoading(false);
        return;
      }
      try {
        const { data } = await api.get('/utilisateurs/moi');
        setUser(data);
      } catch {
        clearTokens();
      } finally {
        setIsLoading(false);
      }
    };
    bootstrap();
  }, []);

  // Appelé après un login / verify-otp réussi
  const login = useCallback((loginResponse) => {
    setTokens(loginResponse);
    if (loginResponse.utilisateur) setUser(loginResponse.utilisateur);
  }, []);

  // Appelé après un logout
  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}