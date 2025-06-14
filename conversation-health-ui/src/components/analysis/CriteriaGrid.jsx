import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/Card";
import Badge from "../ui/Badge";
import ProgressBar from "../ui/ProgressBar";
import {
  getConfidenceBadge,
  formatConfidence,
  formatLabel,
} from "../../utils/helpers";

const CriteriaGrid = ({ results }) => {
  const { criteriaEvaluations } = results;

  return (
    <Card>
      <CardHeader>
        <CardTitle>📊 Evaluation Criteria</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(criteriaEvaluations).map(([key, criteria]) => (
            <CriteriaCard key={key} name={key} criteria={criteria} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

const CriteriaCard = ({ name, criteria }) => {
  const { points, maxPoints, selectedResponse, confidence, reasoning, color } =
    criteria;
  // const percentage = calculatePercentage(points, maxPoints);

  return (
    <div
      className="border border-gray-200 rounded-lg p-4"
      style={{
        borderLeftColor: color,
        borderLeftWidth: "4px",
      }}
    >
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-semibold text-gray-900">{formatLabel(name)}</h4>
        <span className="text-lg font-bold" style={{ color: color }}>
          {points}/{maxPoints}
        </span>
      </div>

      <div className="mb-3">
        <Badge
          className="border"
          style={{
            backgroundColor: color + "20",
            color: color,
            borderColor: color + "40",
          }}
        >
          {selectedResponse.toUpperCase()}
        </Badge>
      </div>

      <div className="flex items-center gap-3 mb-3">
        <div className="flex-grow">
          <ProgressBar
            value={Math.max(0, points)}
            max={maxPoints}
            className="h-2"
            barClassName="transition-all duration-1000 ease-out"
            style={{ backgroundColor: color }}
          />
        </div>
        <Badge className={getConfidenceBadge(confidence)}>
          {formatConfidence(confidence)}
        </Badge>
      </div>

      <p className="text-sm text-gray-600 leading-relaxed">{reasoning}</p>
    </div>
  );
};

export default CriteriaGrid;
