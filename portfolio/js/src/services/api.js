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
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle token refresh and errors
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    const response = await axios.post('/api/v1/auth/refresh', {
                        refresh_token: refreshToken,
                    });

                    const { access_token, refresh_token } = response.data;
                    localStorage.setItem('access_token', access_token);
                    localStorage.setItem('refresh_token', refresh_token);

                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    return api(originalRequest);
                }
            } catch (refreshError) {
                // Refresh failed, redirect to login
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
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

    // Get current user
    getCurrentUser: async () => {
        const response = await api.get('/auth/me');
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
};

// Analytics API methods
export const analyticsAPI = {
    // Get portfolio performance
    getPortfolioPerformance: async (portfolioId, params = {}) => {
        const response = await api.get(`/analytics/performance/${portfolioId}`, { params });
        return response.data;
    },
};

export default api;

