import React from "react";
import { AlertCircle } from "lucide-react";
import { formatLabel } from "../../utils/helpers";

const UncertaintyInfo = ({ results }) => {
  const { uncertaintyInfo } = results;

  if (!uncertaintyInfo) return null;

  const { excludedCriteria, excludedIndicators, lowConfidenceCount } =
    uncertaintyInfo;

  // Don't show if no uncertainty information
  if (
    excludedCriteria.length === 0 &&
    excludedIndicators.length === 0 &&
    !lowConfidenceCount
  ) {
    return null;
  }

  return (
    <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
      <div className="flex items-center gap-2 mb-2">
        <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0" />
        <h4 className="font-medium text-amber-800">Analysis Notes</h4>
      </div>

      <div className="text-sm text-amber-700 space-y-1">
        {excludedCriteria.length > 0 && (
          <p>
            •{" "}
            <span className="font-medium">
              Excluded criteria due to low confidence:
            </span>{" "}
            {excludedCriteria.map(formatLabel).join(", ")}
          </p>
        )}

        {excludedIndicators.length > 0 && (
          <p>
            •{" "}
            <span className="font-medium">
              Excluded indicators due to low confidence:
            </span>{" "}
            {excludedIndicators.map(formatLabel).join(", ")}
          </p>
        )}

        {lowConfidenceCount > 0 && (
          <p>
            •{" "}
            <span className="font-medium">
              {lowConfidenceCount} evaluation(s)
            </span>{" "}
            had lower confidence levels and may require manual review
          </p>
        )}

        <p className="text-xs text-amber-600 mt-2 italic">
          Lower confidence assessments are excluded from final scoring to ensure
          accuracy
        </p>
      </div>
    </div>
  );
};

export default UncertaintyInfo;
