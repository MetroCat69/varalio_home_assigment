import React from "react";
import Select from "../ui/Select";
import { TEST_CASES } from "../../utils/constants";

const TestCaseSelector = ({ selectedTest, onTestChange }) => {
  const handleChange = (e) => {
    onTestChange(e.target.value);
  };

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        Select Test Case
      </label>
      <Select value={selectedTest} onChange={handleChange}>
        <option value="custom">Custom Input</option>
        {Object.entries(TEST_CASES).map(([key, testCase]) => (
          <option key={key} value={key}>
            {testCase.name}
          </option>
        ))}
      </Select>

      {selectedTest &&
        selectedTest !== "custom" &&
        TEST_CASES[selectedTest] && (
          <div className="mt-3 p-3 bg-gray-50 rounded-lg border">
            <p className="text-sm font-medium text-gray-900 mb-1">
              {TEST_CASES[selectedTest].name}
            </p>
            <p className="text-xs text-gray-600 mb-2">
              {TEST_CASES[selectedTest].description}
            </p>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">
                Expected Health Level:
              </span>
              <span className="text-xs font-medium text-gray-700 capitalize">
                {TEST_CASES[selectedTest].expectedHealthLevel}
              </span>
            </div>
          </div>
        )}
    </div>
  );
};

export default TestCaseSelector;
