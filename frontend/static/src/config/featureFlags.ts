// Frontend feature toggles for viewport and material enhancements.
// Flags default to conservative settings to avoid regressions when new integrations land.
export const featureFlags = {
  enableJewelryMaterialEnhancements: false,
  enableHighFidelityViewportLighting: false,
  // Automatically frame camera to fit newly loaded models
  enableAutoFrameOnModelLoad: true,
  // Brighter, higher-contrast grid with gentler fade
  enableBrightGrid: true,
  // Disable HDRI environment to reduce cloudy/foggy reflections on metals
  disableEnvironmentHDRI: true
} as const

export type FeatureFlags = typeof featureFlags
