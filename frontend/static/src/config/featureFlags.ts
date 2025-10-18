// Frontend feature toggles for viewport and material enhancements.
// Professional rendering features enabled for high-quality 3D model visualization.
export const featureFlags = {
  enableJewelryMaterialEnhancements: true,
  enableHighFidelityViewportLighting: true,
  // Automatically frame camera to fit newly loaded models
  enableAutoFrameOnModelLoad: true,
  // Brighter, higher-contrast grid with gentler fade
  enableBrightGrid: true,
  // Enable HDRI environment for professional reflections on metals
  disableEnvironmentHDRI: false
} as const

export type FeatureFlags = typeof featureFlags
