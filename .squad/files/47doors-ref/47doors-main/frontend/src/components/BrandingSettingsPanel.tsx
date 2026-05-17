/**
 * BrandingSettingsPanel - Admin UI for configuring institution branding.
 * Allows CIOs to customize logo, colors, institution name, and tagline.
 */

import { useState, useEffect } from 'react';
import { useBranding } from '../context/BrandingContext';
import {
  PhotoIcon,
  SwatchIcon,
  BuildingLibraryIcon,
  ChatBubbleBottomCenterTextIcon,
  ArrowPathIcon,
  CheckIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';

export function BrandingSettingsPanel() {
  const { branding, isLoading, error, updateBranding, resetBranding } = useBranding();

  // Local form state
  const [logoUrl, setLogoUrl] = useState(branding.logo_url || '');
  const [primaryColor, setPrimaryColor] = useState(branding.primary_color);
  const [institutionName, setInstitutionName] = useState(branding.institution_name);
  const [tagline, setTagline] = useState(branding.tagline);

  // Form status
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Sync form with context when branding changes
  useEffect(() => {
    setLogoUrl(branding.logo_url || '');
    setPrimaryColor(branding.primary_color);
    setInstitutionName(branding.institution_name);
    setTagline(branding.tagline);
  }, [branding]);

  // Check if form has changes
  const hasChanges =
    logoUrl !== (branding.logo_url || '') ||
    primaryColor !== branding.primary_color ||
    institutionName !== branding.institution_name ||
    tagline !== branding.tagline;

  const handleSave = async () => {
    setIsSaving(true);
    setSaveSuccess(false);
    setSaveError(null);

    try {
      await updateBranding({
        logo_url: logoUrl || null,
        primary_color: primaryColor,
        institution_name: institutionName,
        tagline: tagline,
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to save branding');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm('Reset branding to defaults? This cannot be undone.')) {
      return;
    }

    setIsSaving(true);
    setSaveError(null);

    try {
      await resetBranding();
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Failed to reset branding');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h2 className="text-lg font-semibold text-gray-900">Institution Branding</h2>
        <p className="text-sm text-gray-500 mt-1">
          Customize the appearance of the support portal for your institution.
        </p>
      </div>

      {/* Form */}
      <div className="p-6 space-y-6">
        {/* Error display */}
        {(error || saveError) && (
          <div className="flex items-center gap-2 p-3 bg-error-50 border border-error-200 rounded-lg text-error-700">
            <ExclamationCircleIcon className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm">{error || saveError}</span>
          </div>
        )}

        {/* Success display */}
        {saveSuccess && (
          <div className="flex items-center gap-2 p-3 bg-success-50 border border-success-200 rounded-lg text-success-700">
            <CheckIcon className="w-5 h-5 flex-shrink-0" />
            <span className="text-sm">Branding saved successfully!</span>
          </div>
        )}

        {/* Logo URL */}
        <div className="space-y-2">
          <label
            htmlFor="logo-url"
            className="flex items-center gap-2 text-sm font-medium text-gray-700"
          >
            <PhotoIcon className="w-4 h-4" />
            Logo URL
          </label>
          <input
            id="logo-url"
            type="url"
            value={logoUrl}
            onChange={(e) => setLogoUrl(e.target.value)}
            placeholder="https://example.edu/logo.png"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500">
            Enter the URL of your institution's logo. Recommended size: 80x80 pixels.
          </p>
          {logoUrl && (
            <div className="mt-2 p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500 mb-2">Preview:</p>
              <img
                src={logoUrl}
                alt="Logo preview"
                className="w-16 h-16 object-contain rounded-lg border border-gray-200"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = '';
                  (e.target as HTMLImageElement).alt = 'Invalid image URL';
                }}
              />
            </div>
          )}
        </div>

        {/* Primary Color */}
        <div className="space-y-2">
          <label
            htmlFor="primary-color"
            className="flex items-center gap-2 text-sm font-medium text-gray-700"
          >
            <SwatchIcon className="w-4 h-4" />
            Primary Color
          </label>
          <div className="flex items-center gap-3">
            <input
              id="primary-color"
              type="color"
              value={primaryColor}
              onChange={(e) => setPrimaryColor(e.target.value)}
              className="w-12 h-10 rounded-lg border border-gray-300 cursor-pointer"
            />
            <input
              type="text"
              value={primaryColor}
              onChange={(e) => {
                const value = e.target.value;
                if (/^#[0-9A-Fa-f]{0,6}$/.test(value)) {
                  setPrimaryColor(value);
                }
              }}
              placeholder="#2563eb"
              className="w-28 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
            />
            <div
              className="w-10 h-10 rounded-lg border border-gray-200"
              style={{ backgroundColor: primaryColor }}
              title="Color preview"
            />
          </div>
          <p className="text-xs text-gray-500">
            This color will be used for buttons, links, and accents throughout the portal.
          </p>
        </div>

        {/* Institution Name */}
        <div className="space-y-2">
          <label
            htmlFor="institution-name"
            className="flex items-center gap-2 text-sm font-medium text-gray-700"
          >
            <BuildingLibraryIcon className="w-4 h-4" />
            Institution Name
          </label>
          <input
            id="institution-name"
            type="text"
            value={institutionName}
            onChange={(e) => setInstitutionName(e.target.value)}
            placeholder="University Support"
            maxLength={200}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500">
            Displayed in the header. Maximum 200 characters.
          </p>
        </div>

        {/* Tagline */}
        <div className="space-y-2">
          <label
            htmlFor="tagline"
            className="flex items-center gap-2 text-sm font-medium text-gray-700"
          >
            <ChatBubbleBottomCenterTextIcon className="w-4 h-4" />
            Tagline
          </label>
          <input
            id="tagline"
            type="text"
            value={tagline}
            onChange={(e) => setTagline(e.target.value)}
            placeholder="Get help with IT, registration, financial aid, and more"
            maxLength={500}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <p className="text-xs text-gray-500">
            A brief description shown below the institution name. Maximum 500 characters.
          </p>
        </div>

        {/* Live Preview */}
        <div className="space-y-2 pt-4 border-t border-gray-200">
          <h3 className="text-sm font-medium text-gray-700">Live Preview</h3>
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center gap-3">
              {logoUrl ? (
                <img
                  src={logoUrl}
                  alt="Logo preview"
                  className="w-10 h-10 object-contain rounded-lg"
                />
              ) : (
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center"
                  style={{ backgroundColor: primaryColor }}
                >
                  <svg
                    className="w-6 h-6 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                    />
                  </svg>
                </div>
              )}
              <div>
                <h4 className="text-lg font-semibold text-gray-900">
                  {institutionName || 'Institution Name'}
                </h4>
                <p className="text-xs text-gray-500">
                  {tagline || 'Tagline goes here'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
        <button
          type="button"
          onClick={handleReset}
          disabled={isSaving || isLoading}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
        >
          <ArrowPathIcon className="w-4 h-4" />
          Reset to Defaults
        </button>

        <button
          type="button"
          onClick={handleSave}
          disabled={isSaving || isLoading || !hasChanges}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white rounded-lg transition-colors disabled:opacity-50"
          style={{ backgroundColor: hasChanges ? primaryColor : '#9ca3af' }}
        >
          {isSaving ? (
            <>
              <ArrowPathIcon className="w-4 h-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <CheckIcon className="w-4 h-4" />
              Save Changes
            </>
          )}
        </button>
      </div>
    </div>
  );
}
