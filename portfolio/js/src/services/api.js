import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log(`[API] Adding auth token to request: ${config.method?.toUpperCase()} ${config.url}`);
        } else {
            console.log(`[API] No auth token found for request: ${config.method?.toUpperCase()} ${config.url}`);
        }
        return config;
    },
    (error) => {
        console.error('[API] Request interceptor error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor to handle token refresh and errors
api.interceptors.response.use(
    (response) => {
        console.log(`[API] Response received: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
        return response;
    },
    async (error) => {
        console.error(`[API] Response error: ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${error.response?.status}: ${error.response?.data?.detail || error.message}`);
        
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            console.log('[API] Attempting token refresh...');
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    console.log('[API] Refresh token found, attempting refresh...');
                    const response = await authAPI.refreshToken(refreshToken);

                    const { access_token, refresh_token } = response;
                    localStorage.setItem('access_token', access_token);
                    localStorage.setItem('refresh_token', refresh_token);
                    console.log('[API] Token refresh successful');

                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    return api(originalRequest);
                } else {
                    console.log('[API] No refresh token found');
                }
            } catch (refreshError) {
                console.error('[API] Token refresh failed:', refreshError.response?.data || refreshError.message);
                // Refresh failed, redirect to login
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
                localStorage.removeItem('profile');
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

// Authentication API methods
export const authAPI = {
    // User registration
    register: async (userData) => {
        const response = await api.post('/auth/register', userData);
        return response.data;
    },

    // User login
    login: async (credentials) => {
        const response = await api.post('/auth/login', credentials);
        return response.data;
    },

    // User Profile
    getUserProfile: async () => {
        const response = await api.get('/auth/me/profile');
        return response.data;
    },

    // Get current user
    getCurrentUser: async () => {
        const response = await api.get('/auth/me');
        return response.data;
    },

    // Refresh token
    refreshToken: async (refreshToken) => {
        const response = await axios.post('http://localhost:8000/api/v1/auth/refresh', {
            refresh_token: refreshToken,
        });
        return response.data;
    },

    // Logout
    logout: async () => {
        try {
            await api.post('/auth/logout');
        } catch (error) {
            console.warn('Logout API call failed:', error);
        } finally {
            // Always clear local storage
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
        }
    },

    // Forgot password
    forgotPassword: async (email) => {
        const response = await api.post('/auth/forgot-password', { email });
        return response.data;
    },

    // Reset password
    resetPassword: async (resetData) => {
        const response = await api.post('/auth/reset-password', resetData);
        return response.data;
    },

    // Validate reset token
    validateResetToken: async (token) => {
        const response = await api.get(`/auth/validate-reset-token/?token=${token}`);
        return response.data;
    },

    // Change password
    changePassword: async (passwordData) => {
        const response = await api.post('/auth/change-password', passwordData);
        return response.data;
    },

    // Verify email
    verifyEmail: async (token) => {
        const response = await api.post('/auth/verify-email', { token });
        return response.data;
    },

    // Resend email verification
    resendVerification: async () => {
        const response = await api.post('/auth/resend-verification');
        return response.data;
    },
};

// Portfolio API methods
export const portfolioAPI = {
    // Get user portfolios
    getPortfolios: async () => {
        const response = await api.get('/portfolios');
        return response.data;
    },

    // Create portfolio
    createPortfolio: async (portfolioData) => {
        const response = await api.post('/portfolios', portfolioData);
        return response.data;
    },

    // Get portfolio by ID
    getPortfolio: async (id) => {
        const response = await api.get(`/portfolios/${id}`);
        return response.data;
    },

    // Update portfolio
    updatePortfolio: async (id, portfolioData) => {
        const response = await api.put(`/portfolios/${id}`, portfolioData);
        return response.data;
    },

    // Delete portfolio
    deletePortfolio: async (id) => {
        const response = await api.delete(`/portfolios/${id}`);
        return response.data;
    },

    // Get portfolio summary
    getPortfolioSummary: async (id) => {
        const response = await api.get(`/portfolios/${id}/summary`);
        return response.data;
    },
};

// Market data API methods
export const marketAPI = {
    // Get assets
    getAssets: async (params = {}) => {
        const response = await api.get('/assets', { params });
        return response.data;
    },

    // Search assets
    searchAssets: async (query) => {
        const response = await api.get(`/assets/search/${query}`);
        return response.data;
    },

    // Get asset prices
    getAssetPrices: async (id, params = {}) => {
        const response = await api.get(`/assets/${id}/prices`, { params });
        return response.data;
    },

    // Search stock symbols
    searchSymbols: async (query) => {
        const response = await api.get('/stock/symbols', { 
            params: { name: query } 
        });
        return response.data;
    },
};

// Transaction API methods
export const transactionAPI = {
    // Get all transactions
    getTransactions: async (params = {}) => {
        const response = await api.get('/transactions', { params });
        return response.data;
    },

    // Get transactions by portfolio
    getPortfolioTransactions: async (portfolioId, params = {}) => {
        const response = await api.get(`/portfolios/${portfolioId}/transactions`, { params });
        return response.data;
    },

    // Create buy transaction
    createBuyTransaction: async (transactionData) => {
        const response = await api.post('/transactions/buy', transactionData);
        return response.data;
    },

    // Create sell transaction
    createSellTransaction: async (transactionData) => {
        const response = await api.post('/transactions/sell', transactionData);
        return response.data;
    },

    // Get transaction by ID
    getTransaction: async (id) => {
        const response = await api.get(`/transactions/${id}`);
        return response.data;
    },

    // Update transaction
    updateTransaction: async (id, transactionData) => {
        const response = await api.put(`/transactions/${id}`, transactionData);
        return response.data;
    },

    // Delete transaction
    deleteTransaction: async (id) => {
        const response = await api.delete(`/transactions/${id}`);
        return response.data;
    },

    // Get transaction history
    getTransactionHistory: async (params = {}) => {
        const response = await api.get('/transactions/history', { params });
        return response.data;
    },
};

// Analytics API methods
export const analyticsAPI = {
    // Get portfolio performance
    getPortfolioPerformance: async (portfolioId, params = {}) => {
        const response = await api.get(`/analytics/performance/${portfolioId}`, { params });
        return response.data;
    },
};

// Watchlist API methods
export const watchlistAPI = {
    // Get all user watchlists
    getWatchlists: async (includeItems = false) => {
        const response = await api.get('/watchlists', { 
            params: { include_items: includeItems } 
        });
        return response.data;
    },

    // Get specific watchlist
    getWatchlist: async (watchlistId, includeRealTimeData = false) => {
        const response = await api.get(`/watchlists/${watchlistId}`, {
            params: { include_real_time_data: includeRealTimeData }
        });
        return response.data;
    },

    // Create new watchlist
    createWatchlist: async (watchlistData) => {
        const response = await api.post('/watchlists', watchlistData);
        return response.data;
    },

    // Update watchlist
    updateWatchlist: async (watchlistId, updateData) => {
        const response = await api.put(`/watchlists/${watchlistId}`, updateData);
        return response.data;
    },

    // Delete watchlist
    deleteWatchlist: async (watchlistId) => {
        const response = await api.delete(`/watchlists/${watchlistId}`);
        return response.data;
    },

    // Add item to watchlist
    addItemToWatchlist: async (watchlistId, itemData) => {
        const response = await api.post(`/watchlists/${watchlistId}/items`, itemData);
        return response.data;
    },

    // Bulk add items to watchlist
    bulkAddItemsToWatchlist: async (watchlistId, symbols) => {
        const response = await api.post(`/watchlists/${watchlistId}/items/bulk`, { symbols });
        return response.data;
    },

    // Update watchlist item
    updateWatchlistItem: async (watchlistId, itemId, updateData) => {
        const response = await api.put(`/watchlists/${watchlistId}/items/${itemId}`, updateData);
        return response.data;
    },

    // Remove item from watchlist
    removeItemFromWatchlist: async (watchlistId, itemId) => {
        const response = await api.delete(`/watchlists/${watchlistId}/items/${itemId}`);
        return response.data;
    },

    // Reorder watchlist items
    reorderWatchlistItems: async (watchlistId, itemIds) => {
        const response = await api.post(`/watchlists/${watchlistId}/reorder`, { item_ids: itemIds });
        return response.data;
    },

    // Get public watchlists
    getPublicWatchlists: async (limit = 20) => {
        const response = await api.get('/watchlists/public', { params: { limit } });
        return response.data;
    },

    // Get watchlist statistics
    getWatchlistStats: async () => {
        const response = await api.get('/watchlists/stats');
        return response.data;
    },
};

// Utility functions
export const authUtils = {
    // Check if user is authenticated
    isAuthenticated: () => {
        const token = localStorage.getItem('access_token');
        return !!token;
    },

    // Get current access token
    getAccessToken: () => {
        return localStorage.getItem('access_token');
    },

    // Get current refresh token
    getRefreshToken: () => {
        return localStorage.getItem('refresh_token');
    },

    // Clear all auth data
    clearAuth: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        localStorage.removeItem('profile');
    },

    // Check if token is expired (basic check)
    isTokenExpired: (token) => {
        if (!token) return true;
        try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            return payload.exp * 1000 < Date.now();
        } catch (error) {
            console.error('Error parsing token:', error);
            return true;
        }
    }
};

export default api;

