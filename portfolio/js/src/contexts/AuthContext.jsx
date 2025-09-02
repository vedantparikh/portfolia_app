import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authAPI } from '../services/api';

// Action types
const AUTH_ACTIONS = {
    LOGIN_START: 'LOGIN_START',
    LOGIN_SUCCESS: 'LOGIN_SUCCESS',
    LOGIN_FAILURE: 'LOGIN_FAILURE',
    LOGOUT: 'LOGOUT',
    REGISTER_START: 'REGISTER_START',
    REGISTER_SUCCESS: 'REGISTER_SUCCESS',
    REGISTER_FAILURE: 'REGISTER_FAILURE',
    SET_USER: 'SET_USER',
    SET_PROFILE: 'SET_PROFILE',
    CLEAR_ERROR: 'CLEAR_ERROR',
};

// Initial state
const initialState = {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
    isInitialized: false,
};

// Reducer function
const authReducer = (state, action) => {
    switch (action.type) {
        case AUTH_ACTIONS.LOGIN_START:
            return {
                ...state,
                isLoading: true,
                error: null,
            };
        case AUTH_ACTIONS.LOGIN_SUCCESS:
            return {
                ...state,
                user: action.payload.user,
                isAuthenticated: true,
                isLoading: false,
                error: null,
            };
        case AUTH_ACTIONS.LOGIN_FAILURE:
            return {
                ...state,
                isLoading: false,
                error: action.payload,
                isAuthenticated: false,
            };
        case AUTH_ACTIONS.LOGOUT:
            return {
                ...state,
                user: null,
                isAuthenticated: false,
                isLoading: false,
                error: null,
            };
        case AUTH_ACTIONS.REGISTER_START:
            return {
                ...state,
                isLoading: true,
                error: null,
            };
        case AUTH_ACTIONS.REGISTER_SUCCESS:
            return {
                ...state,
                isLoading: false,
                error: null,
            };
        case AUTH_ACTIONS.REGISTER_FAILURE:
            return {
                ...state,
                isLoading: false,
                error: action.payload,
            };
        case AUTH_ACTIONS.SET_USER:
            return {
                ...state,
                user: action.payload,
                isAuthenticated: !!action.payload,
                isInitialized: true,
            };
        case AUTH_ACTIONS.SET_PROFILE:
            return {
                ...state,
                profile: action.payload,
                isAuthenticated: !!action.payload,
                isInitialized: true,
            };
        case AUTH_ACTIONS.CLEAR_ERROR:
            return {
                ...state,
                error: null,
            };
        default:
            return state;
    }
};

// Create context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
    const [state, dispatch] = useReducer(authReducer, initialState);

    // Check if user is already logged in on app start
    useEffect(() => {
        const initializeAuth = async () => {
            try {
                const token = localStorage.getItem('access_token');
                if (token) {
                    const user = await authAPI.getCurrentUser();
                    const profile = await authAPI.getUserProfile();
                    dispatch({ type: AUTH_ACTIONS.SET_USER, payload: user });
                    dispatch({ type: AUTH_ACTIONS.SET_PROFILE, payload: profile });
                } else {
                    dispatch({ type: AUTH_ACTIONS.SET_USER, payload: null });
                }
            } catch (error) {
                console.error('Failed to initialize auth:', error);
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                dispatch({ type: AUTH_ACTIONS.SET_USER, payload: null });
                dispatch({ type: AUTH_ACTIONS.SET_PROFILE, payload: null });
            }
        };

        initializeAuth();
    }, []);

    // Login function
    const login = async (credentials) => {
        try {
            dispatch({ type: AUTH_ACTIONS.LOGIN_START });

            const response = await authAPI.login(credentials);

            // Store tokens
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('refresh_token', response.refresh_token);

            // Get user data
            const user = await authAPI.getCurrentUser();
            const profile = await authAPI.getUserProfile();

            dispatch({ type: AUTH_ACTIONS.SET_USER, payload: user });
            dispatch({ type: AUTH_ACTIONS.SET_PROFILE, payload: profile });
            return { success: true };
        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Login failed';
            dispatch({ type: AUTH_ACTIONS.LOGIN_FAILURE, payload: errorMessage });
            return { success: false, error: errorMessage };
        }
    };

    // Register function
    const register = async (userData) => {
        try {
            dispatch({ type: AUTH_ACTIONS.REGISTER_START });

            await authAPI.register(userData);

            dispatch({ type: AUTH_ACTIONS.REGISTER_SUCCESS });
            return { success: true };
        } catch (error) {
            const errorMessage = error.response?.data?.detail || 'Registration failed';
            dispatch({ type: AUTH_ACTIONS.REGISTER_FAILURE, payload: errorMessage });
            return { success: false, error: errorMessage };
        }
    };

    // Logout function
    const logout = async () => {
        try {
            await authAPI.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            dispatch({ type: AUTH_ACTIONS.LOGOUT });
        }
    };

    // Clear error function
    const clearError = () => {
        dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
    };

    // Context value
    const value = {
        ...state,
        login,
        register,
        logout,
        clearError,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

// Custom hook to use auth context
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

