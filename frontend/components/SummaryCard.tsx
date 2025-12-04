import { ReactNode } from "react";

interface SummaryCardProps {
  title: string;
  value: number;
  currency: string;
  icon: ReactNode;
  color: "success" | "danger" | "primary";
}

export default function SummaryCard({ title, value, currency, icon, color }: SummaryCardProps) {
  const colorClasses = {
    success: "bg-success-50 text-success-700 border-success-200",
    danger: "bg-danger-50 text-danger-700 border-danger-200",
    primary: "bg-primary-50 text-primary-700 border-primary-200",
  };

  return (
    <div className={`bg-white rounded-xl shadow-lg p-6 border-2 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium opacity-80">{title}</h3>
        <div className="opacity-60">{icon}</div>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold">
          {value >= 0 ? "+" : ""}
          {value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </span>
        <span className="text-sm font-medium opacity-70">{currency}</span>
      </div>
    </div>
  );
}

