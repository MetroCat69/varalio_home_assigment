import React from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "../ui/Card";
import Badge from "../ui/Badge";
import {
  getHealthBadge,
  formatHealthLevel,
  getScoreGradient,
} from "../../utils/helpers";
import { cn } from "../../utils/cn";

const OverallScore = ({ results }) => {
  const { finalScore, healthLevel } = results;

  return (
    <Card className="border-l-4 border-indigo-500">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Overall Health Score</CardTitle>
            <CardDescription>
              Comprehensive conversation analysis
            </CardDescription>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold text-indigo-600 mb-2">
              {finalScore}/100
            </div>
            <Badge className={getHealthBadge(healthLevel)}>
              {formatHealthLevel(healthLevel)}
            </Badge>
          </div>
        </div>

        {/* Score Breakdown Bar */}
        <div className="mt-6">
          <div className="flex justify-between text-xs text-gray-500 mb-2">
            <span>Critical (0-24)</span>
            <span>Poor (25-49)</span>
            <span>Concerning (50-69)</span>
            <span>Good (70-84)</span>
            <span>Excellent (85-100)</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div
              className={cn(
                "h-4 rounded-full bg-gradient-to-r transition-all duration-1000 ease-out",
                getScoreGradient(finalScore)
              )}
              style={{
                width: `${finalScore}%`,
                transition: "width 1.5s ease-out",
              }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-600 mt-1">
            <span>0</span>
            <span className="font-medium">{finalScore}</span>
            <span>100</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default OverallScore;
