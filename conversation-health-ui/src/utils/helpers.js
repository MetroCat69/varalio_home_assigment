import { CONFIDENCE_LEVELS, HEALTH_LEVELS } from "./constants";

/**
 * Get Tailwind CSS classes for confidence badge
 */
export const getConfidenceBadge = (confidence) => {
  const level = CONFIDENCE_LEVELS[confidence];
  if (!level) return "bg-gray-100 text-gray-800 border-gray-200";

  const colorMap = {
    emerald: "bg-emerald-100 text-emerald-800 border-emerald-200",
    blue: "bg-blue-100 text-blue-800 border-blue-200",
    yellow: "bg-yellow-100 text-yellow-800 border-yellow-200",
    orange: "bg-orange-100 text-orange-800 border-orange-200",
    red: "bg-red-100 text-red-800 border-red-200",
  };

  return colorMap[level.color] || "bg-gray-100 text-gray-800 border-gray-200";
};

/**
 * Get Tailwind CSS classes for health level badge
 */
export const getHealthBadge = (level) => {
  const healthLevel = HEALTH_LEVELS[level];
  if (!healthLevel) return "bg-gray-100 text-gray-800 border-gray-300";

  const colorMap = {
    green: "bg-green-100 text-green-800 border-green-300",
    blue: "bg-blue-100 text-blue-800 border-blue-300",
    yellow: "bg-yellow-100 text-yellow-800 border-yellow-300",
    orange: "bg-orange-100 text-orange-800 border-orange-300",
    red: "bg-red-100 text-red-800 border-red-300",
  };

  return (
    colorMap[healthLevel.color] || "bg-gray-100 text-gray-800 border-gray-300"
  );
};

/**
 * Format confidence level for display
 */
export const formatConfidence = (confidence) => {
  return (
    CONFIDENCE_LEVELS[confidence]?.label ||
    confidence.replace("_", " ").toUpperCase()
  );
};

/**
 * Format health level for display
 */
export const formatHealthLevel = (level) => {
  return HEALTH_LEVELS[level]?.label || level.toUpperCase();
};

/**
 * Calculate percentage for progress bars
 */
export const calculatePercentage = (value, max) => {
  return Math.round((value / max) * 100);
};

/**
 * Get color for score impact (positive/negative)
 */
export const getImpactColor = (impact) => {
  if (impact > 0) return { bg: "#d1fae5", text: "#10b981" };
  if (impact < 0) return { bg: "#fee2e2", text: "#ef4444" };
  return { bg: "#f3f4f6", text: "#6b7280" };
};

/**
 * Capitalize and format string (replace underscores with spaces)
 */
export const formatLabel = (str) => {
  return str.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
};

/**
 * Get gradient color for health score
 */
export const getScoreGradient = (score) => {
  if (score >= 85) return "from-green-500 to-emerald-500";
  if (score >= 70) return "from-blue-500 to-indigo-500";
  if (score >= 50) return "from-yellow-500 to-orange-500";
  if (score >= 25) return "from-orange-500 to-red-500";
  return "from-red-600 to-red-700";
};
