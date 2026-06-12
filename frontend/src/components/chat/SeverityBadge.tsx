"use client";

import React from "react";

interface SeverityBadgeProps {
  score: number | null;
  className?: string;
}

const SEVERITY_CONFIG: Record<
  number,
  { label: string; className: string; icon: string }
> = {
  1: { label: "Very Mild", className: "med-badge-low", icon: "🟢" },
  2: { label: "Mild", className: "med-badge-low", icon: "🟢" },
  3: { label: "Moderate", className: "med-badge-moderate", icon: "🟡" },
  4: { label: "Severe", className: "med-badge-high", icon: "🔴" },
  5: { label: "Critical", className: "med-badge-critical", icon: "🚨" },
};

export function SeverityBadge({ score, className = "" }: SeverityBadgeProps) {
  if (score === null || score === undefined) return null;

  const config = SEVERITY_CONFIG[score] ?? SEVERITY_CONFIG[2];

  return (
    <span className={`med-badge ${config.className} ${className}`}>
      <span>{config.icon}</span>
      <span>Severity: {score}/5 — {config.label}</span>
    </span>
  );
}
