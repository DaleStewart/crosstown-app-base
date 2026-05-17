/**
 * BrandingContext provides institution branding configuration throughout the app.
 * Handles fetching from API, updating CSS variables, and persisting to localStorage.
 */

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  ReactNode,
} from 'react';
import { getBranding, updateBranding as updateBrandingApi } from '../api/client';
import type { BrandingConfig, BrandingUpdateRequest } from '../types';

const STORAGE_KEY = 'branding-config';

// Default branding configuration
const DEFAULT_BRANDING: BrandingConfig = {
  logo_url: '/47doors-logo.png',
  primary_color: '#2563eb',
  institution_name: '47 Doors',
  tagline: 'University Front Door Support Agent',
};

interface BrandingContextType {
  branding: BrandingConfig;
  isLoading: boolean;
  error: string | null;
  updateBranding: (update: BrandingUpdateRequest) => Promise<void>;
  resetBranding: () => Promise<void>;
  refetchBranding: () => Promise<void>;
}

const BrandingContext = createContext<BrandingContextType | undefined>(undefined);

/**
 * Generate a lighter/darker variant of a hex color.
 */
function adjustColor(hex: string, percent: number): string {
  const num = parseInt(hex.replace('#', ''), 16);
  const amt = Math.round(2.55 * percent);
  const R = Math.min(255, Math.max(0, (num >> 16) + amt));
  const G = Math.min(255, Math.max(0, ((num >> 8) & 0x00ff) + amt));
  const B = Math.min(255, Math.max(0, (num & 0x0000ff) + amt));
  return `#${((1 << 24) | (R << 16) | (G << 8) | B).toString(16).slice(1)}`;
}

/**
 * Apply branding colors to CSS variables on the document root.
 */
function applyBrandingToCSS(branding: BrandingConfig): void {
  const root = document.documentElement;
  const primary = branding.primary_color;

  // Set primary color and variants
  root.style.setProperty('--color-primary', primary);
  root.style.setProperty('--color-primary-hover', adjustColor(primary, -15));
  root.style.setProperty('--color-primary-light', adjustColor(primary, 40));

  // Update Tailwind-like color stops for dynamic theming
  root.style.setProperty('--branding-primary-50', adjustColor(primary, 90));
  root.style.setProperty('--branding-primary-100', adjustColor(primary, 75));
  root.style.setProperty('--branding-primary-200', adjustColor(primary, 55));
  root.style.setProperty('--branding-primary-300', adjustColor(primary, 35));
  root.style.setProperty('--branding-primary-400', adjustColor(primary, 15));
  root.style.setProperty('--branding-primary-500', primary);
  root.style.setProperty('--branding-primary-600', adjustColor(primary, -10));
  root.style.setProperty('--branding-primary-700', adjustColor(primary, -25));
  root.style.setProperty('--branding-primary-800', adjustColor(primary, -40));
  root.style.setProperty('--branding-primary-900', adjustColor(primary, -55));
}

interface BrandingProviderProps {
  children: ReactNode;
}

export function BrandingProvider({ children }: BrandingProviderProps) {
  const [branding, setBranding] = useState<BrandingConfig>(() => {
    // Try to load from localStorage first for instant rendering
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        return JSON.parse(stored);
      }
    } catch {
      // Ignore parse errors
    }
    return DEFAULT_BRANDING;
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch branding from API
  const refetchBranding = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getBranding();
      setBranding(response.config);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(response.config));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch branding';
      setError(message);
      // Keep using cached/default branding on error
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Update branding via API
  const updateBrandingHandler = useCallback(async (update: BrandingUpdateRequest) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await updateBrandingApi(update);
      setBranding(response.config);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(response.config));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update branding';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Reset branding to defaults
  const resetBranding = useCallback(async () => {
    await updateBrandingHandler({
      logo_url: DEFAULT_BRANDING.logo_url,
      primary_color: DEFAULT_BRANDING.primary_color,
      institution_name: DEFAULT_BRANDING.institution_name,
      tagline: DEFAULT_BRANDING.tagline,
    });
  }, [updateBrandingHandler]);

  // Fetch branding on mount
  useEffect(() => {
    refetchBranding();
  }, [refetchBranding]);

  // Apply CSS variables whenever branding changes
  useEffect(() => {
    applyBrandingToCSS(branding);
  }, [branding]);

  const value: BrandingContextType = {
    branding,
    isLoading,
    error,
    updateBranding: updateBrandingHandler,
    resetBranding,
    refetchBranding,
  };

  return (
    <BrandingContext.Provider value={value}>
      {children}
    </BrandingContext.Provider>
  );
}

/**
 * Hook to access branding context.
 */
// eslint-disable-next-line react-refresh/only-export-components
export function useBranding(): BrandingContextType {
  const context = useContext(BrandingContext);
  if (context === undefined) {
    throw new Error('useBranding must be used within a BrandingProvider');
  }
  return context;
}
