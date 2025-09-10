/**
 * ASSET PRELOADER HOOK - React hook for smart asset preloading
 * 
 * This hook provides an easy way to preload assets based on user navigation
 * and interaction patterns. It's designed to improve perceived performance
 * by loading data before users actually need it.
 */

import { useCallback, useEffect } from 'react';
import assetCache from '../services/assetCache';

/**
 * Hook for preloading assets based on user behavior
 * @param {Object} options Configuration options
 * @param {boolean} options.preloadOnMount Whether to preload when component mounts
 * @param {boolean} options.preloadOnHover Whether to preload on hover events
 * @param {Array<string>} options.triggerRoutes Routes that should trigger preloading
 * @returns {Object} Preloading utilities
 */
export const useAssetPreloader = (options = {}) => {
    const {
        preloadOnMount = false,
        preloadOnHover = false,
        triggerRoutes = []
    } = options;

    // Preload assets immediately
    const preloadNow = useCallback(() => {
        assetCache.preloadAssets();
    }, []);

    // Create hover handler for preloading
    const createHoverPreloader = useCallback((delay = 100) => {
        let timeoutId;
        
        return {
            onMouseEnter: () => {
                timeoutId = setTimeout(() => {
                    assetCache.preloadAssets();
                }, delay);
            },
            onMouseLeave: () => {
                if (timeoutId) {
                    clearTimeout(timeoutId);
                }
            }
        };
    }, []);

    // Preload on mount if requested
    useEffect(() => {
        if (preloadOnMount) {
            assetCache.preloadAssets();
        }
    }, [preloadOnMount]);

    // Check if current route should trigger preloading
    useEffect(() => {
        if (triggerRoutes.length > 0) {
            const currentPath = window.location.pathname;
            const shouldPreload = triggerRoutes.some(route => 
                currentPath.includes(route)
            );
            
            if (shouldPreload) {
                assetCache.preloadAssets();
            }
        }
    }, [triggerRoutes]);

    return {
        preloadNow,
        createHoverPreloader,
        getCacheStats: () => assetCache.getStats(),
        clearCache: () => assetCache.clearCache()
    };
};

/**
 * Hook specifically for transaction-related components
 * Automatically preloads assets when used in transaction contexts
 */
export const useTransactionAssetPreloader = () => {
    return useAssetPreloader({
        preloadOnMount: true,
        triggerRoutes: ['/transactions', '/portfolio', '/trade']
    });
};

/**
 * Hook for navigation components (sidebar, menu, etc.)
 * Preloads assets when user hovers over transaction-related navigation items
 */
export const useNavigationPreloader = () => {
    const { createHoverPreloader, preloadNow } = useAssetPreloader();

    // Create hover handlers for different navigation items
    const transactionButtonProps = createHoverPreloader(300); // 300ms delay
    const portfolioButtonProps = createHoverPreloader(500);   // 500ms delay
    const quickCreateProps = createHoverPreloader(100);       // 100ms delay for quick actions

    return {
        transactionButtonProps,
        portfolioButtonProps,
        quickCreateProps,
        preloadNow
    };
};

export default useAssetPreloader;
