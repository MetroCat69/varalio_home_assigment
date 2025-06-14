import React from "react";
import {
  CheckCircle,
  AlertCircle,
  XCircle,
  TrendingUp,
  TrendingDown,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import Badge from "../ui/Badge";
import {
  getConfidenceBadge,
  formatConfidence,
  formatLabel,
  getImpactColor,
} from "../../utils/helpers";

const QualityIndicators = ({ results }) => {
  const { qualityIndicators } = results;

  return (
    <Card>
      <CardHeader>
        <CardTitle>🎯 Quality Indicators</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {Object.entries(qualityIndicators).map(([key, indicator]) => (
            <QualityIndicatorItem key={key} name={key} indicator={indicator} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

const QualityIndicatorItem = ({ name, indicator }) => {
  const { detected, confidence, impact, reasoning, color } = indicator;
  const impactColors = getImpactColor(impact);

  const getIcon = () => {
    if (!detected) return <XCircle className="w-6 h-6 text-gray-400" />;

    if (impact > 0) {
      return <CheckCircle className="w-6 h-6" style={{ color }} />;
    } else if (impact < 0) {
      return <AlertCircle className="w-6 h-6" style={{ color }} />;
    } else {
      return <CheckCircle className="w-6 h-6" style={{ color }} />;
    }
  };

  return (
    <div
      className="flex items-center justify-between p-4 border border-gray-200 rounded-lg transition-all hover:shadow-sm"
      style={{
        borderLeftColor: color,
        borderLeftWidth: "4px",
      }}
    >
      <div className="flex items-center gap-4 flex-grow">
        <div className="flex-shrink-0">{getIcon()}</div>
        <div className="flex-grow min-w-0">
          <div className="flex items-center gap-3 mb-1 flex-wrap">
            <span className="font-semibold text-gray-900">
              {formatLabel(name)}
            </span>
            <Badge className={getConfidenceBadge(confidence)}>
              {formatConfidence(confidence)}
            </Badge>
          </div>
          <p className="text-sm text-gray-600 leading-relaxed">{reasoning}</p>
        </div>
      </div>

      <div className="flex items-center gap-3 flex-shrink-0 ml-4">
        {impact !== 0 && (
          <div
            className="flex items-center gap-1 text-sm font-semibold px-2 py-1 rounded"
            style={{
              color: impactColors.text,
              backgroundColor: impactColors.bg,
            }}
          >
            {impact > 0 ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            {Math.abs(impact)} pts
          </div>
        )}
        <div
          className="w-4 h-4 rounded-full transition-all duration-300"
          style={{
            backgroundColor: detected ? color : "#d1d5db",
          }}
        />
      </div>
    </div>
  );
};

export default QualityIndicators;
