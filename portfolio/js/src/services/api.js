/**
 * API SERVICE - BACKEND COMMUNICATION LAYER
 * 
 * This file handles all communication with the backend server.
 * It provides a centralized way to make HTTP requests to our API.
 * 
 * What this file does:
 * 1. Creates an axios instance with base configuration
 * 2. Sets up request/response interceptors for authentication
 * 3. Handles automatic token refresh
 * 4. Provides organized API methods for different features
 * 5. Manages error handling and token storage
 * 
 * Key concepts for beginners:
 * - Axios: A library for making HTTP requests (like fetch but better)
 * - Interceptors: Functions that run before requests or after responses
 * - JWT Tokens: Secure way to authenticate users
 * - Local Storage: Browser storage that persists between sessions
 * - Promise: JavaScript object representing eventual completion of async operation
 */

// Import axios library for making HTTP requests
import axios from 'axios';

/* 
  CREATE AXIOS INSTANCE - Configure axios with default settings
  This creates a pre-configured axios instance that we can reuse throughout the app
*/
const api = axios.create({
    baseURL: 'http://localhost:8000/api/v1',  // Base URL for all API calls
    timeout: 10000,                           // Request timeout (10 seconds)
    headers: {
        'Content-Type': 'application/json',   // Tell server we're sending JSON data
    },
});

/* 
  REQUEST INTERCEPTOR - Runs before every API request
  This automatically adds the authentication token to all requests
  so we don't have to manually add it to each API call
*/
api.interceptors.request.use(
    (config) => {
        // Get the access token from browser storage
        const token = localStorage.getItem('access_token');
        
        if (token) {
            // If token exists, add it to the request headers
            config.headers.Authorization = `Bearer ${token}`;
            console.log(`[API] Adding auth token to request: ${config.method?.toUpperCase()} ${config.url}`);
        } else {
            // If no token, log that the request will be made without authentication
            console.log(`[API] No auth token found for request: ${config.method?.toUpperCase()} ${config.url}`);
        }
        
        // Return the modified config (with or without token)
        return config;
    },
    (error) => {
        // If there's an error in the request interceptor, log it and reject the promise
        console.error('[API] Request interceptor error:', error);
        return Promise.reject(error);
    }
);

/* 
  RESPONSE INTERCEPTOR - Runs after every API response
  This handles successful responses and errors, including automatic token refresh
*/
api.interceptors.response.use(
    (response) => {
        // Log successful responses for debugging
        console.log(`[API] Response received: ${response.config.method?.toUpperCase()} ${response.config.url} - ${response.status}`);
        return response;
    },
    async (error) => {
        // Log error responses for debugging
        console.error(`[API] Response error: ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${error.response?.status}: ${error.response?.data?.detail || error.message}`);
        
        // Store the original request so we can retry it after token refresh
        const originalRequest = error.config;

        // If we get a 401 (Unauthorized) error and haven't already tried to refresh
        if (error.response?.status === 401 && !originalRequest._retry) {
            console.log('[API] Attempting token refresh...');
            originalRequest._retry = true; // Mark that we're trying to refresh

            try {
                // Get the refresh token from storage
                const refreshToken = localStorage.getItem('refresh_token');
                if (refreshToken) {
                    console.log('[API] Refresh token found, attempting refresh...');
                    
                    // Try to get new tokens using the refresh token
                    const response = await authAPI.refreshToken(refreshToken);

                    // Extract new tokens from response
                    const { access_token, refresh_token } = response;
                    
                    // Save new tokens to storage
                    localStorage.setItem('access_token', access_token);
                    localStorage.setItem('refresh_token', refresh_token);
                    console.log('[API] Token refresh successful');

                    // Add the new token to the original request
                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    
                    // Retry the original request with the new token
                    return api(originalRequest);
                } else {
                    console.log('[API] No refresh token found');
                }
            } catch (refreshError) {
                // If token refresh fails, clear all auth data and redirect to login
                console.error('[API] Token refresh failed:', refreshError.response?.data || refreshError.message);
                
                // Clear all authentication data from storage
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                localStorage.removeItem('user');
                localStorage.removeItem('profile');
                
                // Redirect user to login page
                window.location.href = '/login';
                return Promise.reject(refreshError);
            }
        }

        // If it's not a 401 error or refresh failed, just reject the promise
        return Promise.reject(error);
    }
);

/* 
  AUTHENTICATION API METHODS - User authentication and account management
  These methods handle all authentication-related API calls
*/
export const authAPI = {
    /* 
      USER REGISTRATION - Create a new user account
      Parameters: userData (object with user information)
      Returns: Server response with user data
    */
    register: async (userData) => {
        const response = await api.post('/auth/register', userData);
        return response.data;
    },

    /* 
      USER LOGIN - Authenticate user and get tokens
      Parameters: credentials (object with username and password)
      Returns: Server response with access and refresh tokens
    */
    login: async (credentials) => {
        const response = await api.post('/auth/login', credentials);
        return response.data;
    },

    /* 
      GET USER PROFILE - Get detailed user profile information
      Returns: Server response with user profile data
    */
    getUserProfile: async () => {
        const response = await api.get('/auth/me/profile');
        return response.data;
    },

    /* 
      GET CURRENT USER - Get basic user information
      Returns: Server response with current user data
    */
    getCurrentUser: async () => {
        const response = await api.get('/auth/me');
        return response.data;
    },

    /* 
      REFRESH TOKEN - Get new access token using refresh token
      Parameters: refreshToken (string)
      Returns: Server response with new access and refresh tokens
      Note: This uses direct axios call to avoid interceptor loops
    */
    refreshToken: async (refreshToken) => {
        const response = await axios.post('http://localhost:8000/api/v1/auth/refresh', {
            refresh_token: refreshToken,
        });
        return response.data;
    },

    /* 
      LOGOUT - End user session
      Clears tokens from server and local storage
    */
    logout: async () => {
        try {
            // Try to notify server about logout
            await api.post('/auth/logout');
        } catch (error) {
            // Even if server call fails, we still want to clear local data
            console.warn('Logout API call failed:', error);
        } finally {
            // Always clear local storage regardless of server response
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('user');
        }
    },

    /* 
      FORGOT PASSWORD - Request password reset email
      Parameters: email (string)
      Returns: Server response confirming email was sent
    */
    forgotPassword: async (email) => {
        const response = await api.post('/auth/forgot-password', { email });
        return response.data;
    },

    /* 
      RESET PASSWORD - Set new password using reset token
      Parameters: resetData (object with token and new password)
      Returns: Server response confirming password was reset
    */
    resetPassword: async (resetData) => {
        const response = await api.post('/auth/reset-password', resetData);
        return response.data;
    },

    /* 
      VALIDATE RESET TOKEN - Check if password reset token is valid
      Parameters: token (string)
      Returns: Server response confirming token validity
    */
    validateResetToken: async (token) => {
        const response = await api.get(`/auth/validate-reset-token/?token=${token}`);
        return response.data;
    },

    /* 
      CHANGE PASSWORD - Change password for logged-in user
      Parameters: passwordData (object with old and new passwords)
      Returns: Server response confirming password was changed
    */
    changePassword: async (passwordData) => {
        const response = await api.post('/auth/change-password', passwordData);
        return response.data;
    },

    /* 
      VERIFY EMAIL - Verify user's email address
      Parameters: token (string from verification email)
      Returns: Server response confirming email was verified
    */
    verifyEmail: async (token) => {
        const response = await api.post('/auth/verify-email', { token });
        return response.data;
    },

    /* 
      RESEND VERIFICATION - Send new verification email
      Returns: Server response confirming email was sent
    */
    resendVerification: async () => {
        const response = await api.post('/auth/resend-verification');
        return response.data;
    },
};

/* 
  PORTFOLIO API METHODS - Investment portfolio management
  These methods handle all portfolio-related API calls
*/
export const portfolioAPI = {
    /* 
      GET PORTFOLIOS - Get all portfolios for the current user
      Returns: Server response with array of portfolio objects
    */
    getPortfolios: async () => {
        const response = await api.get('/portfolios');
        return response.data;
    },

    /* 
      CREATE PORTFOLIO - Create a new investment portfolio
      Parameters: portfolioData (object with portfolio information)
      Returns: Server response with created portfolio data
    */
    createPortfolio: async (portfolioData) => {
        const response = await api.post('/portfolios', portfolioData);
        return response.data;
    },

    /* 
      GET PORTFOLIO - Get a specific portfolio by ID
      Parameters: id (string or number)
      Returns: Server response with portfolio details
    */
    getPortfolio: async (id) => {
        const response = await api.get(`/portfolios/${id}`);
        return response.data;
    },

    /* 
      UPDATE PORTFOLIO - Update an existing portfolio
      Parameters: id (string or number), portfolioData (object with updated information)
      Returns: Server response with updated portfolio data
    */
    updatePortfolio: async (id, portfolioData) => {
        const response = await api.put(`/portfolios/${id}`, portfolioData);
        return response.data;
    },

    /* 
      DELETE PORTFOLIO - Delete a portfolio
      Parameters: id (string or number)
      Returns: Server response confirming deletion
    */
    deletePortfolio: async (id) => {
        const response = await api.delete(`/portfolios/${id}`);
        return response.data;
    },

    /* 
      GET PORTFOLIO SUMMARY - Get performance summary for a portfolio
      Parameters: id (string or number)
      Returns: Server response with portfolio performance data
    */
    getPortfolioSummary: async (id) => {
        const response = await api.get(`/portfolios/${id}/summary`);
        return response.data;
    },
};

/* 
  MARKET DATA API METHODS - Stock and asset information
  These methods handle all market data and asset-related API calls
*/
export const marketAPI = {
    /* 
      GET ASSETS - Get list of available assets/stocks
      Parameters: params (object with query parameters like limit, include_prices)
      Returns: Server response with array of asset objects
    */
    getAssets: async (params = {}) => {
        const response = await api.get('/assets', { params });
        return response.data;
    },

    /* 
      SEARCH ASSETS - Search for assets by symbol or name
      Parameters: query (string to search for)
      Returns: Server response with matching assets
    */
    searchAssets: async (query) => {
        const response = await api.get(`/assets/search/${query}`);
        return response.data;
    },

    /* 
      GET ASSET PRICES - Get historical price data for an asset
      Parameters: id (asset ID), params (object with date range, interval)
      Returns: Server response with price history data
    */
    getAssetPrices: async (id, params = {}) => {
        const response = await api.get(`/assets/${id}/prices`, { params });
        return response.data;
    },

    /* 
      SEARCH STOCK SYMBOLS - Search for stock symbols by company name
      Parameters: query (string to search for)
      Returns: Server response with matching stock symbols
    */
    searchSymbols: async (query) => {
        const response = await api.get('/stock/symbols', { 
            params: { name: query } 
        });
        return response.data;
    },
};

/* 
  TRANSACTION API METHODS - Buy/sell transaction management
  These methods handle all transaction-related API calls
*/
export const transactionAPI = {
    /* 
      GET TRANSACTIONS - Get all transactions for the current user
      Parameters: params (object with query parameters like limit, order_by)
      Returns: Server response with array of transaction objects
    */
    getTransactions: async (params = {}) => {
        const response = await api.get('/transactions', { params });
        return response.data;
    },

    /* 
      GET PORTFOLIO TRANSACTIONS - Get transactions for a specific portfolio
      Parameters: portfolioId (string or number), params (query parameters)
      Returns: Server response with array of transaction objects
    */
    getPortfolioTransactions: async (portfolioId, params = {}) => {
        const response = await api.get(`/portfolios/${portfolioId}/transactions`, { params });
        return response.data;
    },

    /* 
      CREATE BUY TRANSACTION - Record a stock purchase
      Parameters: transactionData (object with portfolio_id, symbol, quantity, price, etc.)
      Returns: Server response with created transaction data
    */
    createBuyTransaction: async (transactionData) => {
        const response = await api.post('/transactions/buy', transactionData);
        return response.data;
    },

    /* 
      CREATE SELL TRANSACTION - Record a stock sale
      Parameters: transactionData (object with portfolio_id, symbol, quantity, price, etc.)
      Returns: Server response with created transaction data
    */
    createSellTransaction: async (transactionData) => {
        const response = await api.post('/transactions/sell', transactionData);
        return response.data;
    },

    /* 
      GET TRANSACTION - Get a specific transaction by ID
      Parameters: id (string or number)
      Returns: Server response with transaction details
    */
    getTransaction: async (id) => {
        const response = await api.get(`/transactions/${id}`);
        return response.data;
    },

    /* 
      UPDATE TRANSACTION - Update an existing transaction
      Parameters: id (string or number), transactionData (object with updated information)
      Returns: Server response with updated transaction data
    */
    updateTransaction: async (id, transactionData) => {
        const response = await api.put(`/transactions/${id}`, transactionData);
        return response.data;
    },

    /* 
      DELETE TRANSACTION - Delete a transaction
      Parameters: id (string or number)
      Returns: Server response confirming deletion
    */
    deleteTransaction: async (id) => {
        const response = await api.delete(`/transactions/${id}`);
        return response.data;
    },

    /* 
      GET TRANSACTION HISTORY - Get detailed transaction history
      Parameters: params (object with date range, filters, etc.)
      Returns: Server response with transaction history data
    */
    getTransactionHistory: async (params = {}) => {
        const response = await api.get('/transactions/history', { params });
        return response.data;
    },
};

/* 
  ANALYTICS API METHODS - Performance and analytics data
  These methods handle analytics and performance-related API calls
*/
export const analyticsAPI = {
    /* 
      GET PORTFOLIO PERFORMANCE - Get performance analytics for a portfolio
      Parameters: portfolioId (string or number), params (date range, metrics)
      Returns: Server response with performance data and charts
    */
    getPortfolioPerformance: async (portfolioId, params = {}) => {
        const response = await api.get(`/analytics/performance/${portfolioId}`, { params });
        return response.data;
    },
};

/* 
  WATCHLIST API METHODS - Stock watchlist management
  These methods handle all watchlist-related API calls
*/
export const watchlistAPI = {
    /* 
      GET WATCHLISTS - Get all watchlists for the current user
      Parameters: includeItems (boolean to include watchlist items)
      Returns: Server response with array of watchlist objects
    */
    getWatchlists: async (includeItems = false) => {
        const response = await api.get('/watchlists', { 
            params: { include_items: includeItems } 
        });
        return response.data;
    },

    /* 
      GET WATCHLIST - Get a specific watchlist by ID
      Parameters: watchlistId (string or number), includeRealTimeData (boolean)
      Returns: Server response with watchlist details and items
    */
    getWatchlist: async (watchlistId, includeRealTimeData = false) => {
        const response = await api.get(`/watchlists/${watchlistId}`, {
            params: { include_real_time_data: includeRealTimeData }
        });
        return response.data;
    },

    /* 
      CREATE WATCHLIST - Create a new watchlist
      Parameters: watchlistData (object with name, description, etc.)
      Returns: Server response with created watchlist data
    */
    createWatchlist: async (watchlistData) => {
        const response = await api.post('/watchlists', watchlistData);
        return response.data;
    },

    /* 
      UPDATE WATCHLIST - Update an existing watchlist
      Parameters: watchlistId (string or number), updateData (object with changes)
      Returns: Server response with updated watchlist data
    */
    updateWatchlist: async (watchlistId, updateData) => {
        const response = await api.put(`/watchlists/${watchlistId}`, updateData);
        return response.data;
    },

    /* 
      DELETE WATCHLIST - Delete a watchlist
      Parameters: watchlistId (string or number)
      Returns: Server response confirming deletion
    */
    deleteWatchlist: async (watchlistId) => {
        const response = await api.delete(`/watchlists/${watchlistId}`);
        return response.data;
    },

    /* 
      ADD ITEM TO WATCHLIST - Add a stock to a watchlist
      Parameters: watchlistId (string or number), itemData (object with symbol, notes)
      Returns: Server response with added item data
    */
    addItemToWatchlist: async (watchlistId, itemData) => {
        const response = await api.post(`/watchlists/${watchlistId}/items`, itemData);
        return response.data;
    },

    /* 
      BULK ADD ITEMS - Add multiple stocks to a watchlist at once
      Parameters: watchlistId (string or number), symbols (array of stock symbols)
      Returns: Server response with added items data
    */
    bulkAddItemsToWatchlist: async (watchlistId, symbols) => {
        const response = await api.post(`/watchlists/${watchlistId}/items/bulk`, { symbols });
        return response.data;
    },

    /* 
      UPDATE WATCHLIST ITEM - Update a watchlist item (notes, target price, etc.)
      Parameters: watchlistId (string or number), itemId (string or number), updateData (object)
      Returns: Server response with updated item data
    */
    updateWatchlistItem: async (watchlistId, itemId, updateData) => {
        const response = await api.put(`/watchlists/${watchlistId}/items/${itemId}`, updateData);
        return response.data;
    },

    /* 
      REMOVE ITEM FROM WATCHLIST - Remove a stock from a watchlist
      Parameters: watchlistId (string or number), itemId (string or number)
      Returns: Server response confirming removal
    */
    removeItemFromWatchlist: async (watchlistId, itemId) => {
        const response = await api.delete(`/watchlists/${watchlistId}/items/${itemId}`);
        return response.data;
    },

    /* 
      REORDER WATCHLIST ITEMS - Change the order of items in a watchlist
      Parameters: watchlistId (string or number), itemIds (array of item IDs in new order)
      Returns: Server response confirming reorder
    */
    reorderWatchlistItems: async (watchlistId, itemIds) => {
        const response = await api.post(`/watchlists/${watchlistId}/reorder`, { item_ids: itemIds });
        return response.data;
    },

    /* 
      GET PUBLIC WATCHLISTS - Get publicly shared watchlists
      Parameters: limit (number of watchlists to return)
      Returns: Server response with public watchlists
    */
    getPublicWatchlists: async (limit = 20) => {
        const response = await api.get('/watchlists/public', { params: { limit } });
        return response.data;
    },

    /* 
      GET WATCHLIST STATS - Get statistics about user's watchlists
      Returns: Server response with watchlist statistics
    */
    getWatchlistStats: async () => {
        const response = await api.get('/watchlists/stats');
        return response.data;
    },
};

/* 
  UTILITY FUNCTIONS - Helper functions for authentication
  These are utility functions that can be used throughout the app
*/
export const authUtils = {
    /* 
      IS AUTHENTICATED - Check if user is currently logged in
      Returns: boolean (true if user has access token)
    */
    isAuthenticated: () => {
        const token = localStorage.getItem('access_token');
        return !!token; // Convert to boolean (true if token exists, false if null)
    },

    /* 
      GET ACCESS TOKEN - Get the current access token
      Returns: string (access token) or null
    */
    getAccessToken: () => {
        return localStorage.getItem('access_token');
    },

    /* 
      GET REFRESH TOKEN - Get the current refresh token
      Returns: string (refresh token) or null
    */
    getRefreshToken: () => {
        return localStorage.getItem('refresh_token');
    },

    /* 
      CLEAR AUTH - Remove all authentication data from storage
      This is used when logging out or when tokens are invalid
    */
    clearAuth: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        localStorage.removeItem('profile');
    },

    /* 
      IS TOKEN EXPIRED - Check if a JWT token is expired
      Parameters: token (string) - JWT token to check
      Returns: boolean (true if expired or invalid, false if valid)
      
      Note: This is a basic check. The server should be the final authority on token validity.
    */
    isTokenExpired: (token) => {
        if (!token) return true; // No token means expired
        
        try {
            // JWT tokens have 3 parts separated by dots: header.payload.signature
            // We need the payload (middle part) to check expiration
            const payload = JSON.parse(atob(token.split('.')[1]));
            
            // Check if expiration time (in seconds) is less than current time (in milliseconds)
            return payload.exp * 1000 < Date.now();
        } catch (error) {
            // If we can't parse the token, consider it expired
            console.error('Error parsing token:', error);
            return true;
        }
    }
};

// Export the configured axios instance as default
export default api;

