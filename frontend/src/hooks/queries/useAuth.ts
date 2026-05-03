import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { authApi, type LoginCredentials, type AuthResponse } from '../../api/auth.api';
import api from '../../lib/api';

export interface JwtPayload {
    role: string;
    type: string;
    exp: number;
    user_id?: number;
}

export interface User {
    id: number;
    role: string;
    username: string;
}

interface UseAuthReturn {
    user: User | null;
    isAuthenticated: boolean;
    isAdmin: boolean;
    isLoading: boolean;
    login: (credentials: LoginCredentials) => Promise<AuthResponse>;
    logout: () => Promise<void>;
    getAccessToken: () => string | null;
}

const ACCESS_TOKEN_KEY = 'access_token';
const USER_KEY = 'user';

export const useAuth = (): UseAuthReturn => {
    const navigate = useNavigate();
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(true);

    const parseToken = useCallback((token: string): Omit<User, 'username'> | null => {
        try {
            const decoded = jwtDecode<JwtPayload>(token);
            const isValid = decoded.type === 'access' && decoded.exp * 1000 > Date.now();
            
            if (!isValid) {
                return null;
            }

            return {
                id: decoded.user_id ?? 0,
                role: decoded.role,
            };
        } catch {
            return null;
        }
    }, []);

    const fetchUserInfo = useCallback(async (): Promise<User | null> => {
        try {
            const response = await api.get<User>('/users/me');
            return response.data;
        } catch (error) {
            return null;
        }
    }, []);

    const setAuthData = useCallback(async (token: string) => {
        localStorage.setItem(ACCESS_TOKEN_KEY, token);
        
        const userInfo = await fetchUserInfo();
        
        if (userInfo) {
            localStorage.setItem(USER_KEY, JSON.stringify(userInfo));
            setUser(userInfo);
        } else {
            const parsedUser = parseToken(token);
            if (parsedUser) {
                const partialUser: User = {
                    ...parsedUser,
                    username: `User ${parsedUser.id}`,
                };
                setUser(partialUser);
            }
        }
    }, [fetchUserInfo, parseToken]);

    const clearAuthData = useCallback(() => {
        localStorage.removeItem(ACCESS_TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
        setUser(null);
    }, []);

    const getAccessToken = useCallback((): string | null => {
        return localStorage.getItem(ACCESS_TOKEN_KEY);
    }, []);

    const login = useCallback(async (credentials: LoginCredentials): Promise<AuthResponse> => {
        const response = await authApi.login(credentials);
        
        if (response.access_token) {
            await setAuthData(response.access_token);
        }
        
        return response;
    }, [setAuthData]);

    const logout = useCallback(async (): Promise<void> => {
        try {
            await api.post('/auth/logout');
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            clearAuthData();
            navigate('/login', { replace: true });
        }
    }, [clearAuthData, navigate]);

    useEffect(() => {
        const initAuth = async () => {
            setIsLoading(true);
            
            const storedToken = getAccessToken();
            const storedUser = localStorage.getItem(USER_KEY);
            
            if (storedToken && storedUser) {
                try {
                    const parsedUser = JSON.parse(storedUser);
                    setUser(parsedUser);
                } catch {
                    clearAuthData();
                }
            } else if (storedToken) {
                try {
                    const userInfo = await fetchUserInfo();
                    if (userInfo) {
                        localStorage.setItem(USER_KEY, JSON.stringify(userInfo));
                        setUser(userInfo);
                    } else {
                        clearAuthData();
                    }
                } catch {
                    clearAuthData();
                }
            }
            
            setIsLoading(false);
        };
        
        initAuth();
    }, [getAccessToken, fetchUserInfo, clearAuthData]);

    const isAuthenticated = !!user;
    const isAdmin = user?.role === 'admin';

    return {
        user,
        isAuthenticated,
        isAdmin,
        isLoading,
        login,
        logout,
        getAccessToken,
    };
};