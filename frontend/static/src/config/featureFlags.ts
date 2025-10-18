// Frontend feature toggles for viewport and material enhancements.
// Flags default to conservative settings to avoid regressions when new integrations land.
export const featureFlags = {
  enableJewelryMaterialEnhancements: false,
  enableHighFidelityViewportLighting: false
} as const

export type FeatureFlags = typeof featureFlags
