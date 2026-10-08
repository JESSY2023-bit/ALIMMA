// src/hooks/useAuthContext.js
import { useContext } from 'react';
import { AuthContext } from '../contexts/auth-context';

export const useAuthContext = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthContext doit être utilisé dans <AuthProvider>');
  return ctx;
};