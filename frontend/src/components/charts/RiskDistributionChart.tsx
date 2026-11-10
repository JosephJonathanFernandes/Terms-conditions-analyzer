"use client";

import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
const RISK_COLORS: Record<string, string> = {
  LOW: "#10b981",
  MEDIUM: "#f59e0b",
  HIGH: "#f97316",
  CRITICAL: "#ef4444",
};

interface RiskDistributionChartProps {
  distribution: Record<string, number>;
}

export function RiskDistributionChart({ distribution }: RiskDistributionChartProps) {
  const data = [
    { name: "LOW", value: distribution.LOW || 0, color: RISK_COLORS.LOW },
    { name: "MEDIUM", value: distribution.MEDIUM || 0, color: RISK_COLORS.MEDIUM },
    { name: "HIGH", value: distribution.HIGH || 0, color: RISK_COLORS.HIGH },
    { name: "CRITICAL", value: distribution.CRITICAL || 0, color: RISK_COLORS.CRITICAL },
  ].filter((d) => d.value > 0);

  const total = data.reduce((sum, d) => sum + d.value, 0);

  if (total === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400 text-sm">
        No risk data available
      </div>
    );
  }

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div>
        <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-3">
          Risk Level Distribution
        </h3>
        <div className="h-56">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data} barGap={4}>
              <Tooltip
                content={({ active, payload }: any) => {
                  if (active && payload && payload.length) {
                    const item = payload[0].payload as any;
                    const pct = ((item.value / total) * 100).toFixed(1);
                    return (
                      <div className="bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                        <div className="text-xs font-bold text-navy-900 capitalize">
                          {item.name}
                        </div>
                        <div className="text-xs text-gray-600">
                          {item.value} clause(s) ({(pct)}%)
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-3">
          Risk Composition
        </h3>
        <div className="h-56">
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Tooltip
                content={({ active, payload }: any) => {
                  if (active && payload && payload.length) {
                    const item = payload[0].payload as any;
                    const pct = ((item.value / total) * 100).toFixed(1);
                    return (
                      <div className="bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                        <div className="text-xs font-bold text-navy-900 capitalize">
                          {item.name}
                        </div>
                        <div className="text-xs text-gray-600">
                          {item.value} clause(s) ({(pct)}%)
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                label
              >
                {data.map((d, i) => (
                  <Cell key={`cell-${i}`} fill={d.color} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

interface CategoryChartProps {
  categories: Record<string, number>;
}

export function CategoryDistributionChart({ categories }: CategoryChartProps) {
  const data = Object.entries(categories)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);

  if (data.length === 0) {
    return (
      <div className="h-56 flex items-center justify-center text-gray-400 text-sm">
        No category data available
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wider mb-3">
        Top Clause Categories
      </h3>
      <div className="h-56">
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={data} layout="vertical" barGap={4}>
            <Tooltip />
            <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
